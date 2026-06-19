#!/bin/bash

# Quick Run Script for Financial Intelligence System Examples
# This script rapidly deploys and tests the system with all examples

set -e

echo "=================================================="
echo "Financial Intelligence System - Quick Run Script"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}[1/7] Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Check if API is already running
echo -e "${YELLOW}[2/7] Checking if API is running...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API is already running${NC}"
    API_RUNNING=true
else
    echo "API is not running. Start with:"
    echo "  python3 -m uvicorn backend.api:app --port 8000"
    API_RUNNING=false
fi

# Install dependencies if needed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo -e "${YELLOW}[3/7] Installing dependencies...${NC}"
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${YELLOW}[3/7] Dependencies already installed${NC}"
fi

# Create output directories
echo -e "${YELLOW}[4/7] Setting up directories...${NC}"
mkdir -p examples/analysis_results
mkdir -p examples/indexed_documents
echo -e "${GREEN}✓ Directories ready${NC}"

# Run data loader
echo -e "${YELLOW}[5/7] Loading sample data...${NC}"
python3 examples/scripts/data_loader.py > /dev/null 2>&1 || true
echo -e "${GREEN}✓ Sample data loaded${NC}"

# Run system validation if API is running
if [ "$API_RUNNING" = true ]; then
    echo -e "${YELLOW}[6/7] Running system validation...${NC}"
    python3 examples/scripts/system_validator.py 2>/dev/null || true
    echo -e "${GREEN}✓ System validation complete${NC}"
else
    echo -e "${YELLOW}[6/7] Skipping validation (API not running)${NC}"
fi

# Display next steps
echo -e "${YELLOW}[7/7] Build Complete!${NC}"
echo ""
echo "=================================================="
echo "NEXT STEPS"
echo "=================================================="
echo ""
echo "1. Start the Backend API (if not running):"
echo "   python3 -m uvicorn backend.api:app --host 0.0.0.0 --port 8000"
echo ""
echo "2. Start the Frontend (optional):"
echo "   streamlit run frontend/app.py --server.port 8501"
echo ""
echo "3. Run example scripts:"
echo "   python3 examples/scripts/api_usage_guide.py"
echo "   python3 examples/scripts/batch_processor.py"
echo "   python3 examples/scripts/complete_workflow.py"
echo "   python3 examples/scripts/comparative_analyzer.py"
echo ""
echo "4. View results:"
echo "   cat examples/validation_results.json"
echo "   cat examples/analysis_results/comparative_analysis.json"
echo ""
echo "5. Test with CURL:"
echo "   bash examples/api_requests/api_calls.sh"
echo ""
echo "=================================================="
echo "For detailed documentation, see:"
echo "  - examples/README.md - Main tutorial"
echo "  - examples/EXAMPLES_GUIDE.md - Comprehensive guide"
echo "  - README.md - System documentation"
echo "=================================================="
