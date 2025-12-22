#!/bin/bash
# Download models for deep research orchestrator

set -e

echo "==================================================================="
echo "  Model Download Script"
echo "==================================================================="
echo ""
echo "This script will download:"
echo "  1. Llama-3.1-8B-Abliterated (Fast Agent) - ~7GB"
echo "  2. Qwen2.5-32B-Abliterated (Quality Agent) - ~20GB"
echo ""
echo "Total download size: ~27GB"
echo "Disk space required: ~30GB (with overhead)"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Check if huggingface-cli is installed
if ! command -v huggingface-cli &> /dev/null; then
    echo ""
    echo "→ Installing huggingface-cli..."
    pip install -U "huggingface_hub[cli]"
fi

mkdir -p models

echo ""
echo "==================================================================="
echo "  Downloading Fast Model (Llama 3.1 8B)"
echo "==================================================================="
echo ""

# Note: Check HuggingFace for actual abliterated model repos
# This is a placeholder - update with actual repo

echo "⚠️  NOTE: Please manually download abliterated models from:"
echo ""
echo "Fast Model (8B):"
echo "  → Search HuggingFace for: Llama-3.1-8B-Instruct-Abliterated"
echo "  → Suggested repos: FailSpy, huihui-ai, etc."
echo "  → Download Q6_K quantization (~7GB)"
echo "  → Save to: ./models/Llama-3.1-8B-Instruct-Abliterated-Q6_K.gguf"
echo ""
echo "Quality Model (32B):"
echo "  → Search HuggingFace for: Qwen2.5-32B-Instruct-Abliterated"
echo "  → Download Q4_K_M quantization (~20GB)"
echo "  → Save to: ./models/Qwen2.5-32B-Instruct-Abliterated-Q4_K_M.gguf"
echo ""
echo "Alternatively, download standard models:"
echo ""
echo "# Fast model (standard)"
echo "huggingface-cli download TheBloke/Llama-2-7B-GGUF llama-2-7b.Q6_K.gguf --local-dir models/"
echo ""
echo "# Quality model (standard)"
echo "huggingface-cli download Qwen/Qwen2.5-32B-Instruct-GGUF qwen2_5-32b-instruct-q4_k_m.gguf --local-dir models/"
echo ""
echo "==================================================================="
echo ""
echo "Once downloaded, verify with:"
echo "  ls -lh models/"
echo ""
