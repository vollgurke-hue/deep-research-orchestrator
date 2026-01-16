#!/bin/bash
#
# start_docs_viewer.sh - Deep Research Orchestrator Documentation Viewer
#
# Starts Flask + livereload server for viewing project documentation.
#
# Usage:
#   ./start_docs_viewer.sh              # Default: localhost:8001
#   ./start_docs_viewer.sh --port 9000  # Custom port
#   ./start_docs_viewer.sh --help       # Show help
#

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/viewer/venv"
PYTHON="$VENV_DIR/bin/python3"
PIP="$VENV_DIR/bin/pip"
SERVER_SCRIPT="$SCRIPT_DIR/viewer/serve_docs.py"

echo -e "${BLUE}TPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW${NC}"
echo -e "${BLUE}Q  Deep Research Orchestrator - Documentation Viewer          Q${NC}"
echo -e "${BLUE}ZPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP]${NC}"
echo ""

# Check if venv exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}  Virtual environment not found. Creating...${NC}"
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN} Virtual environment created${NC}"
fi

# Check if dependencies are installed
if ! "$PYTHON" -c "import flask; import livereload" 2>/dev/null; then
    echo -e "${YELLOW}  Dependencies not installed. Installing...${NC}"
    "$PIP" install flask livereload --quiet
    echo -e "${GREEN} Dependencies installed${NC}"
fi

# Check if serve_docs.py exists
if [ ! -f "$SERVER_SCRIPT" ]; then
    echo -e "${RED}L Error: $SERVER_SCRIPT not found${NC}"
    exit 1
fi

# Start server
echo -e "${GREEN}Starting documentation server...${NC}"
echo ""

"$PYTHON" "$SERVER_SCRIPT" "$@"
