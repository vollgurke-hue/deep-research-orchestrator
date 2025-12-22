#!/bin/bash
# Setup llama.cpp with CUDA support

set -e

echo "==================================================================="
echo "  llama.cpp Setup Script"
echo "==================================================================="
echo ""

# Check if already installed
if [ -f "llama.cpp/llama-cli" ]; then
    echo "✓ llama.cpp already installed"
    echo ""
    ./llama.cpp/llama-cli --version
    exit 0
fi

echo "→ Cloning llama.cpp repository..."
git clone https://github.com/ggerganov/llama.cpp.git

cd llama.cpp

echo ""
echo "→ Building with CUDA support (RTX 3060 Ti)..."
echo "  This may take a few minutes..."
echo ""

# Build with CUDA using CMake (new build system)
mkdir -p build
cd build
cmake .. -DGGML_CUDA=ON -DLLAMA_CURL=OFF
cmake --build . --config Release -j $(nproc)

echo ""
echo "==================================================================="
echo "✓ llama.cpp installed successfully!"
echo "==================================================================="
echo ""
echo "Binary location: ./llama.cpp/llama-cli"
echo ""
echo "Test with:"
echo "  ./llama.cpp/llama-cli --version"
echo ""
echo "Next step:"
echo "  ./scripts/download_models.sh"
echo ""
