# 🧞‍♂️ GrocerGenie: AI Grocery Shopping Assistant

GrocerGenie is an intelligent grocery shopping assistant that helps you manage your pantry, plan meals, and shop efficiently. It uses AI to understand natural language and integrates with Kroger's API to add items directly to your cart.

## ✨ Features

- **🤖 AI-Powered Conversations**: Natural language processing for pantry updates and meal planning
- **📦 Smart Pantry Management**: Track what you have and what you need
- **🍳 Intelligent Recipe Creation**: AI generates original recipes based on your available ingredients
- **🛒 Kroger Integration**: Add items directly to your Kroger shopping cart
- **📋 Automatic Shopping Lists**: Generate precise shopping lists from meal plans
- **💾 Session Persistence**: Maintains your pantry and preferences across sessions

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Web browser
- OpenAI API key (optional, but recommended for best experience)

### Installation

1. **Clone or download the project**:
   ```bash
   cd grocer-genie
   ```

2. **Run the setup script** (recommended):
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   Or manually install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your OpenAI API key** (optional but recommended):
   - Get your API key from [OpenAI Platform](https://platform.openai.com/account/api-keys)
   - Create a `.env` file in the `backend` directory:
     ```bash
     cd backend
     echo "OPENAI_API_KEY=your_actual_api_key_here" > .env
     ```

4. **Start the backend server**:
   ```bash
   cd backend
   python app.py
   ```
   The server will start on `http://localhost:5001`

5. **Open the frontend**:
   - Open `frontend/index.html` in your web browser
   - Or serve it with a local server:
     ```bash
     cd frontend
     python -m http.server 8080
     # Then visit http://localhost:8080
     ```

## 🎯 How to Use GrocerGenie

### 1. Managing Your Pantry

**Adding items to your pantry:**
```
You: "I bought 2 onions and a bag of rice"
GrocerGenie: "I've updated your pantry!"
```

**Removing items from your pantry:**
```
You: "I finished the milk and used up 3 eggs"
GrocerGenie: "I've updated your pantry!"
```

**Checking what's in your pantry:**
```
You: "What's in my pantry?"
GrocerGenie: "Your pantry contains: onion: 2, rice: 1"
```

**Natural language variations that work:**
- "I got some chicken and 5 apples"
- "The bread expired and I ran out of cheese"
- "I added 2 tomatoes and used up the onions"
- "My eggs spoiled and I threw away the milk"

### 2. Creating Meal Plans

**Request recipes based on your pantry:**
```
You: "I want to cook something with what I have"
GrocerGenie: [Shows 3 AI-generated recipes using your available ingredients]
```

**Request specific cuisine types:**
```
You: "I want to cook Italian food tonight"
GrocerGenie: [Shows Italian recipes and generates shopping list for missing ingredients]
```

**Other cuisine options:**
- "I want Mexican recipes"
- "Can you suggest Chinese dishes?"
- "I'm in the mood for Italian food"

### 3. Shopping with Kroger Integration

**Set your location:**
```
You: "My zip code is 90210"
GrocerGenie: "Got it! I've set your zip code to 90210."
```

**Add items to your Kroger cart:**
```
You: "Add these items to my cart"
GrocerGenie: "I've added 5 items to your Kroger cart! I couldn't find these items: [list]"
```

**Complete workflow example:**
1. Create a meal plan: "I want Italian recipes"
2. Set your zip code: "My zip code is 90210"
3. Add to cart: "Add these items to my cart"

## 🍳 Recipe Features

### AI-Generated Recipes
GrocerGenie creates original recipes based on your available ingredients:
- **Smart Ingredient Matching**: Uses what you have as the foundation
- **Missing Ingredient Detection**: Identifies what you need to buy
- **Substitution Suggestions**: Recommends alternatives when possible
- **Detailed Instructions**: Step-by-step cooking directions with timing

### Recipe Information
Each recipe includes:
- Creative recipe name
- Ingredient list (marked with what you have vs. need to buy)
- Detailed cooking instructions
- Estimated cooking time
- Cooking tips and variations

## 🛒 Kroger Integration

### How It Works
1. **Location Detection**: Finds the nearest Kroger store using your zip code
2. **Product Search**: Searches Kroger's catalog for your shopping list items
3. **Cart Addition**: Automatically adds found items to your Kroger cart
4. **Missing Items Report**: Tells you which items couldn't be found

### Supported Features
- ✅ Product search by name
- ✅ Location-based store selection
- ✅ Bulk cart addition
- ✅ Missing item reporting

## 🔧 Technical Details

### Backend Architecture
- **Flask Server**: RESTful API endpoints
- **Session Management**: Maintains user state across conversations
- **AI Integration**: OpenAI GPT-4 for natural language processing
- **API Integrations**: TheMealDB for recipes, Kroger for shopping

### Frontend Features
- **Responsive Chat Interface**: Works on desktop and mobile
- **Real-time Communication**: AJAX calls to backend
- **Dynamic Content Rendering**: Different message types (text, recipes, shopping lists)
- **User-friendly Design**: Clean, intuitive interface

### Data Storage
- **Pantry Data**: Stored in `data/pantry.json`
- **Session State**: In-memory conversation context
- **User Preferences**: Zip code and other settings

## 🎨 User Interface

### Chat Interface
- **Message Types**: Text responses, recipe cards, shopping lists
- **Input Methods**: Text area with Enter to send, Shift+Enter for new lines
- **Visual Feedback**: Clear message threading and bot/user distinction

### Recipe Display
- Recipe name and description
- Ingredient list with availability indicators
- Step-by-step cooking instructions
- Cooking time and tips

### Shopping List
- Items needed with quantities
- Integration status with Kroger
- Missing items reporting

## 🔑 Configuration

### Environment Variables
Create a `.env` file in the `backend` directory:

```bash
# Required for AI features (optional but recommended)
OPENAI_API_KEY=your_openai_api_key_here
```

### API Keys
- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/account/api-keys)
- **Kroger Access Token**: Already included in the application (may need refresh for production)

## 🚧 Limitations & Notes

### Current Limitations
- **Kroger Token**: The included token may expire and need refresh
- **Simple Parsing**: Basic natural language processing (enhanced with AI when available)
- **Limited Cuisines**: Focus on Italian, Mexican, and Chinese cuisines
- **Unit Conversions**: No complex ingredient quantity conversions

### Fallback Features
- **No OpenAI Key**: App works with keyword-based parsing
- **API Failures**: Graceful degradation to simpler features
- **Network Issues**: Local pantry management still works

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check Python version
python --version  # Should be 3.7+

# Install dependencies
pip install -r requirements.txt

# Check port availability
# The app runs on port 5001 by default
```

**OpenAI features not working:**
```bash
# Check your .env file
cat backend/.env

# Verify API key is valid
# The app will work with fallback features even without OpenAI
```

**Kroger integration issues:**
- The included token may be expired
- Check your zip code is correct
- Some items may not be available at your local store

**Frontend not connecting:**
- Ensure backend is running on port 5001
- Check browser console for errors
- Try refreshing the page

## 📁 Project Structure

```
grocer-genie/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── conftest.py         # Test configuration
│   ├── test_*.py           # Test files
│   └── .env                # Environment variables (create this)
├── frontend/
│   ├── index.html          # Main HTML file
│   ├── style.css           # Styling
│   ├── script.js           # Frontend JavaScript
│   └── script.test.js      # Frontend tests
├── data/
│   └── pantry.json         # Pantry storage (auto-generated)
├── requirements.txt        # Python dependencies
├── setup.sh               # Setup script
└── README.md              # This file
```

## 🤝 Contributing

This is a demonstration project. Feel free to:
- Enhance the AI features
- Add more recipe sources
- Improve the user interface
- Add more grocery store integrations
- Extend the pantry management features

## 📄 License

This project is for educational and demonstration purposes.

---

**Happy cooking and shopping with GrocerGenie! 🧞‍♂️🛒**