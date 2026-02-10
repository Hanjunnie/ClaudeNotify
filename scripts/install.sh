#!/bin/bash
# Claude Code Notifier - macOS/Linux Install Script

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "============================================================"
echo "  Claude Code Notifier - Install Script"
echo "============================================================"
echo ""

# 프로젝트 루트로 이동
cd "$(dirname "$0")/.."

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            echo "debian"
        elif [ -f /etc/fedora-release ]; then
            echo "fedora"
        elif [ -f /etc/arch-release ]; then
            echo "arch"
        else
            echo "linux"
        fi
    else
        echo "unknown"
    fi
}

OS=$(detect_os)
echo -e "${BLUE}[INFO]${NC} Detected OS: $OS"

# Check Python
echo ""
echo -e "${BLUE}[1/4]${NC} Checking Python..."

if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo "     Python $PYTHON_VERSION found"
else
    echo -e "${RED}[Error]${NC} Python3 is not installed."
    echo ""
    case $OS in
        macos)
            echo "  Install with Homebrew:"
            echo "    brew install python@3.11"
            ;;
        debian)
            echo "  Install with apt:"
            echo "    sudo apt update && sudo apt install python3 python3-pip python3-venv"
            ;;
        fedora)
            echo "  Install with dnf:"
            echo "    sudo dnf install python3 python3-pip"
            ;;
        arch)
            echo "  Install with pacman:"
            echo "    sudo pacman -S python python-pip"
            ;;
        *)
            echo "  Please install Python3 using your package manager."
            ;;
    esac
    exit 1
fi

# Check Python version (3.9+)
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 9 ]); then
    echo -e "${RED}[Error]${NC} Python 3.9 or higher required. Current: $PYTHON_VERSION"
    exit 1
fi

# Linux PyQt6 dependencies
if [[ "$OS" == "debian" ]]; then
    echo ""
    echo -e "${BLUE}[INFO]${NC} Checking PyQt6 system dependencies..."
    DEPS_NEEDED=()
    for pkg in libxcb-xinerama0 libxcb-cursor0 libxkbcommon-x11-0; do
        if ! dpkg -s $pkg &> /dev/null; then
            DEPS_NEEDED+=($pkg)
        fi
    done
    if [ ${#DEPS_NEEDED[@]} -gt 0 ]; then
        echo -e "${YELLOW}[Warning]${NC} Missing system packages: ${DEPS_NEEDED[*]}"
        read -p "     Install them? (y/N): " INSTALL_DEPS
        if [[ "$INSTALL_DEPS" =~ ^[Yy]$ ]]; then
            sudo apt update
            sudo apt install -y ${DEPS_NEEDED[*]}
        fi
    fi
fi

# Setup virtual environment
echo ""
echo -e "${BLUE}[2/4]${NC} Setting up virtual environment..."

VENV_DIR=""
CREATE_VENV=false

if [ -d "venv" ]; then
    VENV_DIR="venv"
    echo "     Existing venv found"
    read -p "     Recreate virtual environment? (y/N): " RECREATE
    if [[ "$RECREATE" =~ ^[Yy]$ ]]; then
        rm -rf venv
        CREATE_VENV=true
    fi
elif [ -d ".venv" ]; then
    VENV_DIR=".venv"
    echo "     Existing .venv found"
    read -p "     Recreate virtual environment? (y/N): " RECREATE
    if [[ "$RECREATE" =~ ^[Yy]$ ]]; then
        rm -rf .venv
        CREATE_VENV=true
        VENV_DIR="venv"
    fi
else
    CREATE_VENV=true
    VENV_DIR="venv"
fi

if [ "$CREATE_VENV" = true ]; then
    echo "     Creating virtual environment..."
    $PYTHON_CMD -m venv $VENV_DIR
    echo "     Virtual environment created"
fi

# Install dependencies
echo ""
echo -e "${BLUE}[3/4]${NC} Installing dependencies..."
source $VENV_DIR/bin/activate

pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

# Verify installation
echo ""
echo -e "${BLUE}[4/4]${NC} Verifying installation..."
python -c "from PyQt6.QtCore import PYQT_VERSION_STR; print(f'     PyQt6 {PYQT_VERSION_STR} installed')"
python -c "import watchdog; print('     watchdog installed')"

chmod +x scripts/run.sh

echo ""
echo "============================================================"
echo -e "  ${GREEN}Installation complete!${NC}"
echo "============================================================"
echo ""
echo "  To run:"
echo "    ./scripts/run.sh"
echo ""
echo "============================================================"
echo ""
