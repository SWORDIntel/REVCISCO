"""
Robust serial port connection handler for direct TTY connection to Cisco router
"""

import serial
import serial.tools.list_ports
import time
import threading
import queue
import os
import sys
from pathlib import Path
from typing import Optional, List, Callable, Any
import fcntl
import termios
import struct

try:
    import termios
    TIOCSBRK = termios.TIOCSBRK
    TIOCCBRK = termios.TIOCCBRK
except (ImportError, AttributeError):
    # Fallback values for Linux
    TIOCSBRK = 0x5427
    TIOCCBRK = 0x5428


class SerialConnection:
    """Robust serial port connection handler"""
    
    def __init__(self, port: Optional[str] = None, baudrate: int = 9600,
                 logger: Optional[Any] = None, metrics: Optional[Any] = None):
        self.port = port
        self.baudrate = baudrate
        self.logger = logger
        self.metrics = metrics
        
        self.serial_port: Optional[serial.Serial] = None
        self.output_queue: queue.Queue = queue.Queue()
        self.output_buffer: str = ""
        self.read_thread: Optional[threading.Thread] = None
        self.reading_active = False
        self.connection_start_time: Optional[float] = None
        
    def detect_ports(self) -> List[str]:
        """Detect available TTY ports"""
        ports = []
        
        # Scan common TTY port patterns
        tty_patterns = ['/dev/ttyS*', '/dev/ttyUSB*', '/dev/ttyACM*']
        
        for pattern in tty_patterns:
            import glob
            found_ports = glob.glob(pattern)
            ports.extend(found_ports)
        
        # Also use pyserial's list_ports
        try:
            pyserial_ports = serial.tools.list_ports.comports()
            for port_info in pyserial_ports:
                if port_info.device not in ports:
                    ports.append(port_info.device)
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Error listing ports with pyserial: {e}")
        
        # Filter out non-existent ports and sort
        existing_ports = [p for p in ports if Path(p).exists()]
        return sorted(set(existing_ports))
    
    def select_port(self, ports: Optional[List[str]] = None) -> Optional[str]:
        """Select port from available ports"""
        if ports is None:
            ports = self.detect_ports()
        
        if not ports:
            if self.logger:
                self.logger.error("No TTY ports found")
            return None
        
        if len(ports) == 1:
            selected = ports[0]
            if self.logger:
                self.logger.info(f"Auto-selected single port: {selected}")
            return selected
        
        # Multiple ports - return first for now (TUI will handle selection)
        if self.logger:
            self.logger.info(f"Found {len(ports)} ports: {', '.join(ports)}")
        return ports[0]  # Default to first, TUI can override
    
    def open(self, port: Optional[str] = None, baudrate: Optional[int] = None) -> bool:
        """Open serial port connection"""
        if port:
            self.port = port
        if baudrate:
            self.baudrate = baudrate
        
        if not self.port:
            self.port = self.select_port()
            if not self.port:
                return False
        
        try:
            # Validate port exists
            if not Path(self.port).exists():
                if self.logger:
                    self.logger.error(f"Port {self.port} does not exist")
                return False
            
            # Open serial port with Cisco console settings
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1.0,  # Read timeout
                write_timeout=1.0,  # Write timeout
                xonxoff=False,  # Software flow control disabled
                rtscts=False,  # Hardware flow control disabled
                dsrdtr=False  # DSR/DTR flow control disabled
            )
            
            # Flush buffers
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            
            self.connection_start_time = time.time()
            if self.metrics:
                self.metrics.start_connection()
            
            # Start output capture thread
            self.reading_active = True
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
            
            if self.logger:
                self.logger.info(f"Opened serial port {self.port} at {self.baudrate} baud")
                self.logger.log_operation("serial_open", f"Opened port {self.port}", success=True)
            
            return True
            
        except serial.SerialException as e:
            if self.logger:
                self.logger.error(f"Failed to open port {self.port}: {e}")
                if "Permission denied" in str(e):
                    self.logger.error("Permission denied. Try adding user to dialout group: sudo usermod -a -G dialout $USER")
                elif "Device or resource busy" in str(e):
                    self.logger.error("Port is busy. Close other applications using this port.")
            return False
        except Exception as e:
            if self.logger:
                self.logger.log_exception(e, "opening serial port")
            return False
    
    def close(self):
        """Close serial port connection"""
        self.reading_active = False
        
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2.0)
        
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
                if self.logger:
                    self.logger.info(f"Closed serial port {self.port}")
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Error closing port: {e}")
        
        self.serial_port = None
    
    def _read_loop(self):
        """Background thread to continuously read from serial port"""
        while self.reading_active and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    if data:
                        text = data.decode('utf-8', errors='replace')
                        self.output_buffer += text
                        self.output_queue.put(text)
                        
                        if self.logger:
                            self.logger.log_command(text, direction="RECEIVED")
                            if self.logger.log_level <= 10:  # DEBUG
                                self.logger.log_hex_dump(data, "Received")
                        
                        if self.metrics:
                            self.metrics.record_bytes(received=len(data))
                else:
                    time.sleep(0.01)  # Small delay when no data
            except serial.SerialException:
                break
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Error in read loop: {e}")
                time.sleep(0.1)
    
    def read_output(self, timeout: float = 1.0) -> str:
        """Read output from queue with timeout"""
        output = ""
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            try:
                chunk = self.output_queue.get(timeout=0.1)
                output += chunk
            except queue.Empty:
                continue
        
        return output
    
    def get_output_buffer(self) -> str:
        """Get current output buffer"""
        return self.output_buffer
    
    def clear_output_buffer(self):
        """Clear output buffer"""
        self.output_buffer = ""
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
            except queue.Empty:
                break
    
    def write(self, data: str) -> int:
        """Write data to serial port"""
        if not self.serial_port or not self.serial_port.is_open:
            if self.logger:
                self.logger.error("Serial port not open")
            return 0
        
        try:
            # Ensure proper line ending
            if not data.endswith('\r') and not data.endswith('\n'):
                data += '\r'
            
            written = self.serial_port.write(data.encode('utf-8'))
            self.serial_port.flush()
            
            if self.logger:
                self.logger.log_command(data, direction="SENT")
                if self.logger.log_level <= 10:  # DEBUG
                    self.logger.log_hex_dump(data.encode('utf-8'), "Sent")
            
            if self.metrics:
                self.metrics.record_bytes(sent=written)
            
            return written
        except serial.SerialException as e:
            if self.logger:
                self.logger.error(f"Error writing to port: {e}")
            return 0
    
    def send_break_standard(self, duration: float = 0.25) -> bool:
        """Send break sequence using standard pyserial method"""
        if not self.serial_port or not self.serial_port.is_open:
            return False
        
        try:
            start_time = time.time()
            self.serial_port.send_break(duration=duration)
            elapsed = time.time() - start_time
            
            if self.logger:
                self.logger.debug(f"Sent break sequence (standard method, {duration}s)")
                self.metrics.record_break_attempt("standard", elapsed, True, time.time())
            
            return True
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Standard break failed: {e}")
                self.metrics.record_break_attempt("standard", 0, False, time.time())
            return False
    
    def send_break_ioctl(self, duration: float = 0.25) -> bool:
        """Send break sequence using low-level ioctl"""
        if not self.serial_port or not self.serial_port.is_open:
            return False
        
        try:
            fd = self.serial_port.fileno()
            start_time = time.time()
            
            # Set break
            fcntl.ioctl(fd, TIOCSBRK)
            time.sleep(duration)
            # Clear break
            fcntl.ioctl(fd, TIOCCBRK)
            
            elapsed = time.time() - start_time
            
            if self.logger:
                self.logger.debug(f"Sent break sequence (ioctl method, {duration}s)")
                self.metrics.record_break_attempt("ioctl", elapsed, True, time.time())
            
            return True
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Ioctl break failed: {e}")
                self.metrics.record_break_attempt("ioctl", 0, False, time.time())
            return False
    
    def send_break_extended(self, duration: float = 0.5) -> bool:
        """Send extended break sequence"""
        return self.send_break_standard(duration=duration)
    
    def send_break_multiple(self, count: int = 3, duration: float = 0.1, gap: float = 0.05) -> bool:
        """Send multiple rapid break sequences"""
        success = False
        for i in range(count):
            if self.send_break_standard(duration=duration):
                success = True
            if i < count - 1:
                time.sleep(gap)
        return success
    
    def send_break_signal_toggle(self) -> bool:
        """Send break by toggling DTR/RTS signals"""
        if not self.serial_port or not self.serial_port.is_open:
            return False
        
        try:
            start_time = time.time()
            
            # Toggle DTR
            self.serial_port.dtr = False
            time.sleep(0.1)
            self.serial_port.dtr = True
            time.sleep(0.1)
            
            # Toggle RTS
            self.serial_port.rts = False
            time.sleep(0.1)
            self.serial_port.rts = True
            
            elapsed = time.time() - start_time
            
            if self.logger:
                self.logger.debug("Sent break sequence (signal toggle method)")
                self.metrics.record_break_attempt("signal_toggle", elapsed, True, time.time())
            
            return True
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Signal toggle break failed: {e}")
                self.metrics.record_break_attempt("signal_toggle", 0, False, time.time())
            return False
    
    def send_break(self, method: Optional[str] = None, duration: float = 0.25) -> bool:
        """
        Send break sequence using specified method or try all methods
        
        Methods tried in order:
        1. standard - pyserial send_break()
        2. extended - longer duration standard break
        3. multiple - multiple rapid breaks
        4. ioctl - low-level ioctl
        5. signal_toggle - DTR/RTS toggle
        """
        methods = [
            ("standard", lambda: self.send_break_standard(duration)),
            ("extended", lambda: self.send_break_extended(duration * 2)),
            ("multiple", lambda: self.send_break_multiple(3, 0.1, 0.05)),
            ("ioctl", lambda: self.send_break_ioctl(duration)),
            ("signal_toggle", self.send_break_signal_toggle),
        ]
        
        if method:
            # Try specific method
            for name, func in methods:
                if name == method:
                    return func()
            return False
        else:
            # Try all methods in order
            for name, func in methods:
                if func():
                    if self.logger:
                        self.logger.info(f"Break sequence successful using {name} method")
                    return True
                time.sleep(0.1)  # Small delay between attempts
            
            if self.logger:
                self.logger.error("All break sequence methods failed")
            return False
    
    def is_open(self) -> bool:
        """Check if port is open"""
        return self.serial_port is not None and self.serial_port.is_open
    
    def flush(self):
        """Flush input and output buffers"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            self.clear_output_buffer()
