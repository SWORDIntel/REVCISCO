#!/bin/bash
#
# Cisco 4321 ISR Password Reset Tool - Bootstrap Script
# This script sets up the complete environment for the tool
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
VENV_DIR="venv"
PYTHON_MIN_VERSION="3.7"
REQUIREMENTS_FILE="requirements.txt"
SRC_DIR="src"

# Print functions
print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# Check if running as root
check_not_root() {
    if [ "$EUID" -eq 0 ]; then
        print_error "Do not run this script as root!"
        print_info "Run as your regular user. The script will prompt for sudo when needed."
        exit 1
    fi
}

# Check Python version
check_python() {
    print_header "Checking Python Installation"
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed!"
        print_info "Please install Python 3.7 or higher:"
        print_info "  Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
        print_info "  Fedora/RHEL: sudo dnf install python3 python3-pip"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    REQUIRED_MAJOR=$(echo $PYTHON_MIN_VERSION | cut -d. -f1)
    REQUIRED_MINOR=$(echo $PYTHON_MIN_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt "$REQUIRED_MAJOR" ] || \
       ([ "$PYTHON_MAJOR" -eq "$REQUIRED_MAJOR" ] && [ "$PYTHON_MINOR" -lt "$REQUIRED_MINOR" ]); then
        print_error "Python $PYTHON_VERSION is installed, but Python $PYTHON_MIN_VERSION or higher is required!"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION found"
    PYTHON_CMD="python3"
}

# Create virtual environment
create_venv() {
    print_header "Setting Up Virtual Environment"
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists"
        read -p "Recreate virtual environment? [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Removing existing virtual environment..."
            rm -rf "$VENV_DIR"
        else
            print_info "Using existing virtual environment"
            return 0
        fi
    fi
    
    print_info "Creating virtual environment..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    
    if [ ! -d "$VENV_DIR" ]; then
        print_error "Failed to create virtual environment!"
        exit 1
    fi
    
    print_success "Virtual environment created"
}

# Activate virtual environment
activate_venv() {
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
        print_success "Virtual environment activated"
    else
        print_error "Virtual environment activation script not found!"
        exit 1
    fi
}

# Upgrade pip
upgrade_pip() {
    print_info "Upgrading pip..."
    pip install --upgrade pip --quiet
    print_success "pip upgraded"
}

# Install dependencies
install_dependencies() {
    print_header "Installing Dependencies"
    
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        print_error "Requirements file not found: $REQUIREMENTS_FILE"
        exit 1
    fi
    
    print_info "Installing packages from $REQUIREMENTS_FILE..."
    pip install -r "$REQUIREMENTS_FILE"
    
    print_success "Dependencies installed"
}

# Create directory structure
create_directories() {
    print_header "Creating Directory Structure"
    
    DIRS=("logs" "monitoring" "backups" "config")
    
    for dir in "${DIRS[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_info "Created directory: $dir"
        else
            print_info "Directory exists: $dir"
        fi
    done
    
    print_success "Directory structure ready"
}

# Setup user permissions
setup_user_permissions() {
    print_header "Setting Up User Permissions"
    
    # Check if user is in dialout group (for serial port access)
    if groups | grep -q "\bdialout\b"; then
        print_success "User is already in dialout group"
    else
        print_warning "User is not in dialout group (required for serial port access)"
        print_info "Adding user to dialout group..."
        
        if command -v sudo &> /dev/null; then
            sudo usermod -a -G dialout "$USER"
            print_success "User added to dialout group"
            print_warning "You may need to log out and back in for changes to take effect"
        else
            print_error "sudo not available. Please run manually:"
            print_info "  sudo usermod -a -G dialout $USER"
            print_info "  Then log out and back in"
        fi
    fi
}

# Make scripts executable
make_executable() {
    print_header "Setting Script Permissions"
    
    SCRIPTS=("src/bootstrap.py" "src/main.py" "src/cisco_reset.py" "scripts/test_tool.py")
    
    for script in "${SCRIPTS[@]}"; do
        if [ -f "$script" ]; then
            chmod +x "$script"
            print_info "Made executable: $script"
        fi
    done
    
    chmod +x "$0"  # Make bootstrap.sh executable
    print_success "Script permissions set"
}

# Verify installation
verify_installation() {
    print_header "Verifying Installation"
    
    # Check if we're in venv
    if [ -z "$VIRTUAL_ENV" ]; then
        print_error "Virtual environment not activated!"
        return 1
    fi
    
    # Test imports
    print_info "Testing Python imports..."
    python3 -c "
import sys
from pathlib import Path
src_dir = Path('$SRC_DIR').resolve()
sys.path.insert(0, str(src_dir))
try:
    from logging_monitor import LoggingMonitor
    from prompt_detector import PromptDetector
    print('✓ Core modules import successfully')
except ImportError as e:
    print(f'✗ Import error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
" || {
        print_error "Import test failed!"
        return 1
    }
    
    print_success "Installation verified"
}

# Create activation script
create_activate_script() {
    print_header "Creating Activation Script"
    
    ACTIVATE_SCRIPT="activate.sh"
    cat > "$ACTIVATE_SCRIPT" << EOF
#!/bin/bash
# Activation script for Cisco Reset Tool
# Source this file to activate the virtual environment

SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
cd "\$SCRIPT_DIR"

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
    echo "Run: python src/bootstrap.py"
    echo "Or: python src/main.py"
else
    echo "Error: Virtual environment not found!"
    echo "Run: ./bootstrap.sh first"
    return 1
fi
EOF
    
    chmod +x "$ACTIVATE_SCRIPT"
    print_success "Activation script created: $ACTIVATE_SCRIPT"
}

# Main installation function
main() {
    print_header "Cisco 4321 ISR Password Reset Tool - Bootstrap"
    
    print_info "Script directory: $SCRIPT_DIR"
    print_info "User: $USER"
    print_info "Home: $HOME"
    
    # Check not running as root
    check_not_root
    
    # Check Python
    check_python
    
    # Create virtual environment
    create_venv
    
    # Activate virtual environment
    activate_venv
    
    # Upgrade pip
    upgrade_pip
    
    # Install dependencies
    install_dependencies
    
    # Create directories
    create_directories
    
    # Setup user permissions
    setup_user_permissions
    
    # Make scripts executable
    make_executable
    
    # Create activation script
    create_activate_script
    
    # Verify installation
    verify_installation
    
    # Final message
    print_header "Bootstrap Complete!"
    
    echo -e "${GREEN}Setup completed successfully!${NC}\n"
    echo -e "To use the tool:"
    echo -e "  1. Activate the virtual environment:"
    echo -e "     ${CYAN}source venv/bin/activate${NC}"
    echo -e "  2. Or use the activation script:"
    echo -e "     ${CYAN}source activate.sh${NC}"
    echo -e "  3. Run the tool:"
    echo -e "     ${CYAN}python src/bootstrap.py${NC}"
    echo -e "     ${CYAN}python src/main.py${NC}"
    echo -e "\nOr run directly:"
    echo -e "     ${CYAN}./bootstrap.sh && source venv/bin/activate && python src/bootstrap.py${NC}"
    echo ""
    
    # Ask if user wants to run the tool now
    read -p "Run the tool now? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Launching tool..."
        python src/bootstrap.py
    fi
}

# Run main function
main "$@"
