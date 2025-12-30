#!/bin/bash

# 🎬 Narratives Media - Lead Icebreaker Generator
# Mac এ run করতে এই script টি ব্যবহার করো

echo ""
echo "🎬 ═══════════════════════════════════════════════════════"
echo "   Narratives Media - Lead Icebreaker Generator"
echo "═══════════════════════════════════════════════════════"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 পাওয়া যায়নি!"
    echo ""
    echo "Install করতে Terminal এ এই command দাও:"
    echo "   brew install python3"
    echo ""
    exit 1
fi

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment তৈরি হচ্ছে..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Virtual environment activate হচ্ছে..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Dependencies install হচ্ছে..."
pip install -r requirements.txt --quiet

# Run the app
echo ""
echo "✅ App চালু হচ্ছে!"
echo ""
echo "🌐 Browser এ এই link খোলো:"
echo "   http://localhost:8501"
echo ""
echo "বন্ধ করতে: Ctrl+C"
echo ""

streamlit run app.py --server.headless true
