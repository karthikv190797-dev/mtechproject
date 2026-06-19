#!/bin/bash
# Quick Models Setup Guide
# Run this to initialize and test the models directory

set -e  # Exit on error

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║         🎯 MODELS DIRECTORY SETUP & VERIFICATION                  ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="/usr/local/bin/python3"

# Step 1: Check model registry
echo "📋 Step 1: Check Model Registry"
echo "─────────────────────────────────────────────────────────"
$PYTHON models/model_loader.py
echo ""

# Step 2: Information
echo "📚 Step 2: Data & Documents"
echo "─────────────────────────────────────────────────────────"
if [ -d "data" ]; then
    echo "✅ Data directory exists"
    echo "   Documents found:"
    find data -type f \( -name "*.txt" -o -name "*.json" -o -name "*.md" \) | sed 's/^/      /'
else
    echo "ℹ️  Data directory not found at $(pwd)/data"
fi
echo ""

# Step 3: Create FAISS index
echo "🔍 Step 3: Create FAISS Index"
echo "─────────────────────────────────────────────────────────"
if [ -d "data" ]; then
    echo "Creating FAISS index from data/documents..."
    $PYTHON models/create_faiss_index.py --documents data --model all-MiniLM-L6-v2 --output models/embeddings/all-MiniLM-L6-v2
    FAISS_READY=$?
    if [ $FAISS_READY -eq 0 ]; then
        echo "✅ FAISS index created successfully"
    else
        echo "⚠️  FAISS index creation had issues (check output above)"
    fi
else
    echo "ℹ️  Skipping FAISS creation (no data/ directory)"
fi
echo ""

# Step 4: Final summary
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║               ✅ MODELS DIRECTORY READY TO USE                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📦 Available Directories:"
echo "   • models/embeddings/          — Vector embeddings and FAISS indices"
echo "   • models/reasoning/           — Teacher/Student distillation models"
echo "   • models/retrievers/          — Retriever configurations (BM25, FAISS, Hybrid)"
echo "   • models/checkpoints/         — Training checkpoints and logs"
echo ""
echo "🚀 Quick Start:"
echo "   1. Load embeddings:"
echo "      from models.model_loader import ModelLoader"
echo "      loader = ModelLoader()"
echo "      embedder = loader.get_embedding_model('all-MiniLM-L6-v2')"
echo ""
echo "   2. Create/Load FAISS index:"
echo "      python models/create_faiss_index.py"
echo "      index = loader.get_faiss_index('all-MiniLM-L6-v2')"
echo ""
echo "   3. Load reasoning models:"
echo "      teacher = loader.get_reasoning_model('teacher_model')"
echo ""
echo "📖 Documentation:"
echo "   • models/README.md — Main overview"
echo "   • models/embeddings/README.md — Embeddings guide"
echo "   • models/reasoning/README.md — Reasoning models guide"
echo "   • models/retrievers/README.md — Retriever configurations"
echo "   • models/checkpoints/README.md — Training checkpoints"
echo ""
