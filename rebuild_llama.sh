#!/bin/bash
set -e

echo "Building llama.cpp for RTX 3060 Ti (CUDA 86) + GTX 1060 (CUDA 61)..."
cd /home/phili/Schreibtisch/AI_Projects/deep-research-orchestrator/llama.cpp/build

cmake --build . --config Release -j 16

echo ""
echo "✓ Build complete!"
echo ""
ls -lh bin/llama-server
