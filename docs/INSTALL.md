# Installation Guide

## Quick Install

```bash
./bootstrap.sh
```

That's it! The bootstrap script handles everything.

## What Bootstrap Does

1. **Checks Python Version** (requires 3.7+)
2. **Creates Virtual Environment** (`venv/`)
3. **Installs Dependencies** (pyserial, rich, textual)
4. **Creates Directories** (logs/, monitoring/, backups/, config/)
5. **Sets Up User** (adds to dialout group for serial port access)
6. **Makes Scripts Executable**
7. **Verifies Installation**

## Manual Installation (if needed)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Add user to dialout group
sudo usermod -a -G dialout $USER
# Log out and back in

# Create directories
mkdir -p logs monitoring backups config
```

## After Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Run tool
python src/bootstrap.py
```

## Troubleshooting

### Bootstrap fails
- Check Python version: `python3 --version` (needs 3.7+)
- Check internet connection (for pip install)
- Check sudo access (for dialout group)

### Import errors after bootstrap
- Make sure venv is activated: `source venv/bin/activate`
- Re-run bootstrap: `./bootstrap.sh`

### Permission errors
- User must be in dialout group
- After adding: log out and back in
- Check: `groups | grep dialout`
