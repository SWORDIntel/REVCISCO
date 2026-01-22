"""
Comprehensive system detection and inventory module
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from command_executor import CommandExecutor


class SystemDetector:
    """System detection and inventory"""
    
    def __init__(self, command_executor: CommandExecutor, logger: Optional[Any] = None,
                 metrics: Optional[Any] = None):
        self.command_executor = command_executor
        self.logger = logger
        self.metrics = metrics
        self.detection_results: Dict[str, Any] = {}
        
    def detect_all(self) -> Dict[str, Any]:
        """Run all detection operations"""
        if self.logger:
            self.logger.info("Starting comprehensive system detection...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'licenses': self.detect_licenses(),
            'hardware': self.detect_hardware(),
            'software': self.detect_software(),
            'features': self.detect_features(),
            'interfaces': self.detect_interfaces(),
            'modules': self.detect_modules(),
            'configuration': self.detect_configuration(),
            'system_info': self.detect_system_info()
        }
        
        self.detection_results = results
        
        if self.logger:
            self.logger.info("System detection complete")
        
        return results
    
    def detect_licenses(self) -> Dict[str, Any]:
        """Detect license information"""
        if self.logger:
            self.logger.info("Detecting licenses...")
        
        licenses = {
            'license_summary': None,
            'license_features': None,
            'license_udi': None,
            'license_details': None,
            'parsed': {
                'active_licenses': [],
                'inactive_licenses': [],
                'evaluation_licenses': [],
                'udi': {}
            }
        }
        
        # show license summary
        try:
            success, output = self.command_executor.execute("show license summary", timeout=10.0)
            if success:
                licenses['license_summary'] = output
                self._parse_license_summary(output, licenses['parsed'])
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to get license summary: {e}")
        
        # show license feature
        try:
            success, output = self.command_executor.execute("show license feature", timeout=10.0)
            if success:
                licenses['license_features'] = output
                self._parse_license_features(output, licenses['parsed'])
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to get license features: {e}")
        
        # show license udi
        try:
            success, output = self.command_executor.execute("show license udi", timeout=10.0)
            if success:
                licenses['license_udi'] = output
                self._parse_license_udi(output, licenses['parsed'])
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to get license UDI: {e}")
        
        return licenses
    
    def _parse_license_summary(self, output: str, parsed: Dict):
        """Parse license summary output"""
        # Look for license status patterns
        active_pattern = re.compile(r'Status:\s*ACTIVE', re.IGNORECASE)
        inactive_pattern = re.compile(r'Status:\s*INACTIVE', re.IGNORECASE)
        eval_pattern = re.compile(r'Status:\s*EVALUATION', re.IGNORECASE)
        
        lines = output.split('\n')
        for line in lines:
            if active_pattern.search(line):
                parsed['active_licenses'].append(line.strip())
            elif inactive_pattern.search(line):
                parsed['inactive_licenses'].append(line.strip())
            elif eval_pattern.search(line):
                parsed['evaluation_licenses'].append(line.strip())
    
    def _parse_license_features(self, output: str, parsed: Dict):
        """Parse license features output"""
        # Extract feature information
        feature_pattern = re.compile(r'([A-Za-z0-9_-]+)\s+.*?(\d+)\s+(\w+)', re.IGNORECASE)
        matches = feature_pattern.findall(output)
        for match in matches:
            feature_name = match[0]
            count = match[1]
            status = match[2]
            parsed['active_licenses'].append({
                'feature': feature_name,
                'count': count,
                'status': status
            })
    
    def _parse_license_udi(self, output: str, parsed: Dict):
        """Parse license UDI output"""
        # Extract UDI information
        pid_pattern = re.compile(r'PID:\s*([A-Z0-9-]+)', re.IGNORECASE)
        sn_pattern = re.compile(r'SN:\s*([A-Z0-9]+)', re.IGNORECASE)
        
        pid_match = pid_pattern.search(output)
        sn_match = sn_pattern.search(output)
        
        if pid_match:
            parsed['udi']['pid'] = pid_match.group(1)
        if sn_match:
            parsed['udi']['sn'] = sn_match.group(1)
    
    def detect_hardware(self) -> Dict[str, Any]:
        """Detect hardware inventory"""
        if self.logger:
            self.logger.info("Detecting hardware inventory...")
        
        hardware = {
            'inventory': None,
            'version': None,
            'hardware_details': None,
            'diag': None,
            'parsed': {
                'chassis': {},
                'modules': [],
                'interfaces': [],
                'memory': {},
                'cpu': {},
                'flash': {}
            }
        }
        
        # show inventory
        try:
            success, output = self.command_executor.execute("show inventory", timeout=15.0)
            if success:
                hardware['inventory'] = output
                self._parse_inventory(output, hardware['parsed'])
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to get inventory: {e}")
        
        # show version
        try:
            success, output = self.command_executor.execute("show version", timeout=10.0)
            if success:
                hardware['version'] = output
                self._parse_version(output, hardware['parsed'])
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to get version: {e}")
        
        return hardware
    
    def _parse_inventory(self, output: str, parsed: Dict):
        """Parse inventory output"""
        # Extract chassis and module information
        name_pattern = re.compile(r'NAME:\s*"([^"]+)"', re.IGNORECASE)
        desc_pattern = re.compile(r'DESCR:\s*"([^"]+)"', re.IGNORECASE)
        pid_pattern = re.compile(r'PID:\s*([A-Z0-9-]+)', re.IGNORECASE)
        vid_pattern = re.compile(r'VID:\s*([A-Z0-9]+)', re.IGNORECASE)
        sn_pattern = re.compile(r'SN:\s*([A-Z0-9]+)', re.IGNORECASE)
        
        lines = output.split('\n')
        current_item = {}
        
        for line in lines:
            name_match = name_pattern.search(line)
            if name_match:
                if current_item:
                    if 'Chassis' in current_item.get('name', ''):
                        parsed['chassis'] = current_item
                    else:
                        parsed['modules'].append(current_item)
                current_item = {'name': name_match.group(1)}
            
            if current_item:
                desc_match = desc_pattern.search(line)
                if desc_match:
                    current_item['description'] = desc_match.group(1)
                
                pid_match = pid_pattern.search(line)
                if pid_match:
                    current_item['pid'] = pid_match.group(1)
                
                sn_match = sn_pattern.search(line)
                if sn_match:
                    current_item['sn'] = sn_match.group(1)
        
        if current_item:
            if 'Chassis' in current_item.get('name', ''):
                parsed['chassis'] = current_item
            else:
                parsed['modules'].append(current_item)
    
    def _parse_version(self, output: str, parsed: Dict):
        """Parse version output"""
        # Extract system information
        uptime_pattern = re.compile(r'uptime is\s+(.+)', re.IGNORECASE)
        memory_pattern = re.compile(r'(\d+[KMGT]?) bytes of (?:.*?memory|RAM)', re.IGNORECASE)
        processor_pattern = re.compile(r'processor.*?(\d+)\s*MHz', re.IGNORECASE)
        
        uptime_match = uptime_pattern.search(output)
        if uptime_match:
            parsed['uptime'] = uptime_match.group(1).strip()
        
        memory_match = memory_pattern.search(output)
        if memory_match:
            parsed['memory']['total'] = memory_match.group(1)
        
        processor_match = processor_pattern.search(output)
        if processor_match:
            parsed['cpu']['speed'] = processor_match.group(1)
    
    def detect_software(self) -> Dict[str, Any]:
        """Detect software version and packages"""
        if self.logger:
            self.logger.info("Detecting software version...")
        
        software = {
            'version': None,
            'software_packages': None,
            'parsed': {
                'ios_version': None,
                'image_file': None,
                'packages': []
            }
        }
        
        # show version
        try:
            success, output = self.command_executor.execute("show version", timeout=10.0)
            if success:
                software['version'] = output
                self._parse_software_version(output, software['parsed'])
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to get version: {e}")
        
        # show software (IOS XE)
        try:
            success, output = self.command_executor.execute("show software", timeout=15.0)
            if success:
                software['software_packages'] = output
                self._parse_software_packages(output, software['parsed'])
        except Exception as e:
            if self.logger:
                self.logger.debug(f"show software not available (may not be IOS XE): {e}")
        
        return software
    
    def _parse_software_version(self, output: str, parsed: Dict):
        """Parse software version"""
        # Extract IOS version
        version_pattern = re.compile(r'Version\s+([0-9.()A-Za-z]+)', re.IGNORECASE)
        image_pattern = re.compile(r'System image file is\s+"([^"]+)"', re.IGNORECASE)
        
        version_match = version_pattern.search(output)
        if version_match:
            parsed['ios_version'] = version_match.group(1)
        
        image_match = image_pattern.search(output)
        if image_match:
            parsed['image_file'] = image_match.group(1)
    
    def _parse_software_packages(self, output: str, parsed: Dict):
        """Parse software packages (IOS XE)"""
        # Extract package information
        package_pattern = re.compile(r'([A-Za-z0-9_-]+)\s+.*?(\d+\.\d+\.\d+)', re.IGNORECASE)
        matches = package_pattern.findall(output)
        for match in matches:
            parsed['packages'].append({
                'name': match[0],
                'version': match[1]
            })
    
    def detect_features(self) -> Dict[str, Any]:
        """Detect enabled features"""
        if self.logger:
            self.logger.info("Detecting features...")
        
        features = {
            'feature_list': None,
            'running_config': None,
            'parsed': {
                'security_features': [],
                'routing_protocols': [],
                'switching_features': [],
                'voice_features': [],
                'wireless_features': []
            }
        }
        
        # show feature (IOS XE)
        try:
            success, output = self.command_executor.execute("show feature", timeout=10.0)
            if success:
                features['feature_list'] = output
        except Exception as e:
            if self.logger:
                self.logger.debug(f"show feature not available: {e}")
        
        # Parse running config for features
        try:
            success, output = self.command_executor.execute("show running-config", timeout=30.0)
            if success:
                features['running_config'] = output[:10000]  # Limit size
                self._parse_config_features(output, features['parsed'])
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to get running config: {e}")
        
        return features
    
    def _parse_config_features(self, output: str, parsed: Dict):
        """Parse features from configuration"""
        # Detect routing protocols
        routing_protocols = ['ospf', 'eigrp', 'bgp', 'rip', 'isis']
        for protocol in routing_protocols:
            if re.search(rf'\b{protocol}\b', output, re.IGNORECASE):
                parsed['routing_protocols'].append(protocol.upper())
        
        # Detect security features
        if re.search(r'\bipsec\b', output, re.IGNORECASE):
            parsed['security_features'].append('IPSEC')
        if re.search(r'\bssl\b', output, re.IGNORECASE):
            parsed['security_features'].append('SSL')
    
    def detect_interfaces(self) -> Dict[str, Any]:
        """Detect interfaces"""
        if self.logger:
            self.logger.info("Detecting interfaces...")
        
        interfaces = {
            'interface_brief': None,
            'parsed': {
                'physical': [],
                'logical': [],
                'summary': {}
            }
        }
        
        # show ip interface brief
        try:
            success, output = self.command_executor.execute("show ip interface brief", timeout=15.0)
            if success:
                interfaces['interface_brief'] = output
                self._parse_interface_brief(output, interfaces['parsed'])
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to get interface brief: {e}")
        
        return interfaces
    
    def _parse_interface_brief(self, output: str, parsed: Dict):
        """Parse interface brief output"""
        lines = output.split('\n')
        for line in lines:
            # Skip header lines
            if 'Interface' in line and 'IP-Address' in line:
                continue
            
            # Parse interface line
            parts = line.split()
            if len(parts) >= 4:
                interface = {
                    'name': parts[0],
                    'ip_address': parts[1] if parts[1] != 'unassigned' else None,
                    'status': parts[2] if len(parts) > 2 else None,
                    'protocol': parts[3] if len(parts) > 3 else None
                }
                
                if interface['name'].startswith(('GigabitEthernet', 'FastEthernet', 'Serial', 'Ethernet')):
                    parsed['physical'].append(interface)
                else:
                    parsed['logical'].append(interface)
        
        parsed['summary'] = {
            'total_physical': len(parsed['physical']),
            'total_logical': len(parsed['logical'])
        }
    
    def detect_modules(self) -> Dict[str, Any]:
        """Detect installed modules"""
        # Modules are detected in hardware inventory
        return self.detection_results.get('hardware', {}).get('parsed', {}).get('modules', [])
    
    def detect_configuration(self) -> Dict[str, Any]:
        """Detect configuration summary"""
        if self.logger:
            self.logger.info("Detecting configuration summary...")
        
        config = {
            'hostname': None,
            'domain': None,
            'summary': {}
        }
        
        # show running-config (limited)
        try:
            success, output = self.command_executor.execute("show running-config | include hostname", timeout=10.0)
            if success:
                hostname_match = re.search(r'hostname\s+(\S+)', output, re.IGNORECASE)
                if hostname_match:
                    config['hostname'] = hostname_match.group(1)
        except Exception as e:
            if self.logger:
                self.logger.debug(f"Failed to get hostname: {e}")
        
        return config
    
    def detect_system_info(self) -> Dict[str, Any]:
        """Detect system information"""
        if self.logger:
            self.logger.info("Detecting system information...")
        
        info = {
            'clock': None,
            'users': None,
            'memory': None,
            'flash': None
        }
        
        # show clock
        try:
            success, output = self.command_executor.execute("show clock", timeout=5.0)
            if success:
                info['clock'] = output.strip()
        except Exception as e:
            if self.logger:
                self.logger.debug(f"Failed to get clock: {e}")
        
        # show users
        try:
            success, output = self.command_executor.execute("show users", timeout=5.0)
            if success:
                info['users'] = output
        except Exception as e:
            if self.logger:
                self.logger.debug(f"Failed to get users: {e}")
        
        return info
    
    def export_results(self, format: str = "json", filename: Optional[str] = None) -> str:
        """Export detection results"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"detection_{timestamp}.{format}"
        
        output_file = Path("monitoring") / filename
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            with open(output_file, 'w') as f:
                json.dump(self.detection_results, f, indent=2)
        elif format == "yaml":
            try:
                import yaml
                with open(output_file, 'w') as f:
                    yaml.dump(self.detection_results, f, default_flow_style=False)
            except ImportError:
                if self.logger:
                    self.logger.warning("PyYAML not installed, cannot export YAML")
                return ""
        elif format == "txt":
            with open(output_file, 'w') as f:
                f.write(self._format_text_report())
        else:
            if self.logger:
                self.logger.error(f"Unsupported export format: {format}")
            return ""
        
        if self.logger:
            self.logger.info(f"Detection results exported to {output_file}")
        
        return str(output_file)
    
    def _format_text_report(self) -> str:
        """Format detection results as text report"""
        report = []
        report.append("=" * 80)
        report.append("Cisco Router System Detection Report")
        report.append("=" * 80)
        report.append(f"Timestamp: {self.detection_results.get('timestamp', 'Unknown')}")
        report.append("")
        
        # Licenses
        licenses = self.detection_results.get('licenses', {})
        report.append("LICENSES")
        report.append("-" * 80)
        if licenses.get('parsed', {}).get('udi'):
            udi = licenses['parsed']['udi']
            report.append(f"UDI: PID={udi.get('pid', 'N/A')}, SN={udi.get('sn', 'N/A')}")
        report.append("")
        
        # Hardware
        hardware = self.detection_results.get('hardware', {})
        report.append("HARDWARE")
        report.append("-" * 80)
        if hardware.get('parsed', {}).get('chassis'):
            chassis = hardware['parsed']['chassis']
            report.append(f"Chassis: {chassis.get('name', 'N/A')}")
            report.append(f"  Description: {chassis.get('description', 'N/A')}")
            report.append(f"  PID: {chassis.get('pid', 'N/A')}")
            report.append(f"  SN: {chassis.get('sn', 'N/A')}")
        report.append("")
        
        # Software
        software = self.detection_results.get('software', {})
        report.append("SOFTWARE")
        report.append("-" * 80)
        if software.get('parsed', {}).get('ios_version'):
            report.append(f"IOS Version: {software['parsed']['ios_version']}")
        if software.get('parsed', {}).get('image_file'):
            report.append(f"Image File: {software['parsed']['image_file']}")
        report.append("")
        
        # Interfaces
        interfaces = self.detection_results.get('interfaces', {})
        report.append("INTERFACES")
        report.append("-" * 80)
        summary = interfaces.get('parsed', {}).get('summary', {})
        report.append(f"Physical Interfaces: {summary.get('total_physical', 0)}")
        report.append(f"Logical Interfaces: {summary.get('total_logical', 0)}")
        report.append("")
        
        report.append("=" * 80)
        return "\n".join(report)
    
    def get_results(self) -> Dict[str, Any]:
        """Get detection results"""
        return self.detection_results
