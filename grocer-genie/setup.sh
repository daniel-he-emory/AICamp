#!/bin/bash

echo "🧞‍♂️ Setting up GrocerGenie..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "🔑 Creating .env file..."
    cat > backend/.env << EOF
# OpenAI API Key - Get yours from https://platform.openai.com/account/api-keys
# Replace 'your_openai_api_key_here' with your actual API key
OPENAI_API_KEY=your_openai_api_key_here
EOF
    echo "✅ Created backend/.env file"
    echo "⚠️  Please edit backend/.env and add your OpenAI API key"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🚀 Setup complete! To run the application:"
echo "1. Edit backend/.env and add your OpenAI API key"
echo "2. Run: cd backend && python app.py"
echo "3. Open frontend/index.html in your browser"
echo ""
echo "💡 If you don't have an OpenAI API key, the app will still work with fallback features!" 