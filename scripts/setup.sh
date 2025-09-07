#!/bin/bash
# RedFlag Development Environment Setup Script

set -e  # Exit on any error

echo "🚀 Setting up RedFlag development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check Python version
echo "🐍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    print_error "Python ${PYTHON_VERSION} detected. Please install Python ${REQUIRED_VERSION} or higher."
    exit 1
fi

print_status "Python ${PYTHON_VERSION} detected"

# Create virtual environment
echo "📦 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📚 Installing core dependencies..."
pip install -r requirements.txt

echo "🛠️  Installing development dependencies..."
pip install -r requirements-dev.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating environment configuration..."
    cp .env.example .env
    print_warning "Please edit .env with your API keys before running the application"
else
    print_warning ".env file already exists"
fi

# Set up pre-commit hooks
echo "🎣 Setting up pre-commit hooks..."
pre-commit install
print_status "Pre-commit hooks installed"

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p data/{raw,processed,assets/{screenshots,logos},reports,archive}
mkdir -p logs
mkdir -p temp

print_status "Project directories created"

# Check for required system dependencies
echo "🔍 Checking system dependencies..."

# Check for Chrome/Chromium (needed for Selenium)
if command -v google-chrome &> /dev/null; then
    print_status "Google Chrome found"
elif command -v chromium-browser &> /dev/null; then
    print_status "Chromium browser found"
else
    print_warning "Chrome/Chromium not found. Install for Selenium WebDriver:"
    echo "  - macOS: brew install --cask google-chrome"
    echo "  - Ubuntu: sudo apt install google-chrome-stable"
    echo "  - Or download from: https://www.google.com/chrome/"
fi

# Validate API keys setup
echo "🔑 Checking API configuration..."
if grep -q "your_.*_key_here" .env; then
    print_warning "Please update your API keys in .env file:"
    echo "  - SERPAPI_KEY: Get from https://serpapi.com/dashboard"
    echo "  - GOOGLE_PAGESPEED_API_KEY: Get from Google Cloud Console"
    echo "  - BUILTWITH_API_KEY: Get from https://api.builtwith.com/"
else
    print_status "API keys appear to be configured"
fi

# Test basic imports
echo "🧪 Testing basic imports..."
python3 -c "
try:
    import requests
    import pandas as pd
    import selenium
    from PIL import Image
    print('✅ All core dependencies imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys"
echo "2. Activate the environment: source venv/bin/activate"
echo "3. Run a test script: python demo_bakersfield_gyms.py"
echo ""
echo "For more information, see README.md"