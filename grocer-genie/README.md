# 🧞‍♂️ GrocerGenie: AI Grocery Shopping Assistant

GrocerGenie is a smart shopping assistant that streamlines meal planning through a conversational interface. It helps you manage your pantry inventory, plan meals with recipes, generate precise shopping lists, and add items directly to your Kroger cart.

## ✨ Features

- **Conversational Pantry Management**: Update your pantry inventory through natural language
- **Smart Meal Planning**: Get recipe suggestions from TheMealDB API
- **Intelligent Shopping Lists**: Compare ingredients with your pantry to generate precise shopping lists
- **Kroger Integration**: Add items directly to your Kroger cart using their API
- **Session State Management**: Maintains context across conversations

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Kroger API access token (provided in the project)

### Installation

1. **Clone the repository**:
   ```bash
   cd grocer-genie
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Flask backend**:
   ```bash
   cd backend
   python app.py
   ```
   The backend will run on `http://localhost:5000`

4. **Open the frontend**:
   - Open `frontend/index.html` in your web browser
   - Or serve it with a local server:
     ```bash
     cd frontend
     python -m http.server 8080
     ```
   - Then visit `http://localhost:8080`

## 🎯 Usage Examples

### 1. Managing Your Pantry

```
User: "I just bought 2 onions and a bag of rice, and I finished the milk"
GrocerGenie: "OK, I've added 2 onions and 1 bag of rice to your pantry and removed the milk."

User: "What's in my pantry?"
GrocerGenie: "Your pantry contains: onion: 2, rice: 1"
```

### 2. Creating Meal Plans

```
User: "I want some Italian recipes for dinner"
GrocerGenie: [Shows 3 Italian recipes with images and ingredients]

User: "Can you suggest some Mexican dishes?"
GrocerGenie: [Shows Mexican recipes and generates shopping list]
```

### 3. Adding to Kroger Cart

```
User: "Add these items to my cart"
GrocerGenie: "I need your zip code to find a nearby Kroger store. What is your zip code?"

User: "90210"
GrocerGenie: "I've added 5 items to your Kroger cart! I couldn't find these items: [list]"
```

## 🏗️ Architecture

### Backend (Flask)
- **Session State Management**: Tracks pantry, meal plans, and shopping lists
- **Intent Recognition**: Simple keyword-based classification of user messages
- **API Integrations**: TheMealDB for recipes, Kroger API for shopping
- **Entity Extraction**: Parses food items and quantities from natural language

### Frontend (Vanilla JS)
- **Chat Interface**: Clean, responsive chat UI
- **Dynamic Rendering**: Different message types (text, meal plans, shopping lists)
- **Real-time Communication**: AJAX calls to backend API

### Data Storage
- **pantry.json**: Persistent pantry inventory storage
- **Session State**: In-memory conversation context

## 🔧 API Endpoints

- `POST /chat-with-agent`: Main conversational endpoint
- `POST /set-zipcode`: Set user's zip code for Kroger integration

## 🛠️ Technical Implementation

### Intent Recognition
The system recognizes these intents from user messages:
- `update_pantry`: Add/remove items from pantry
- `check_pantry`: View current pantry contents
- `request_meal_plan`: Get recipe suggestions
- `add_to_cart`: Add shopping list items to Kroger cart
- `clarification`: Handle unclear requests

### Kroger Integration
- **Location Finding**: Find nearest store by zip code
- **Product Search**: Search Kroger's product catalog
- **Cart Management**: Add items to user's Kroger cart

### Ingredient Matching
Smart ingredient comparison between recipes and pantry:
- Basic name matching with normalization
- Synonym recognition
- Quantity checking
- Shopping list generation for missing items

## 📁 Project Structure

```
grocer-genie/
├── backend/
│   └── app.py              # Flask application
├── frontend/
│   ├── index.html          # Main HTML file
│   ├── style.css           # Styling
│   └── script.js           # Frontend JavaScript
├── data/
│   └── pantry.json         # Pantry storage (auto-generated)
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔑 Environment Variables

The Kroger API access token is currently hardcoded in the application. For production use, set it as an environment variable:

```bash
export KROGER_ACCESS_TOKEN="your_token_here"
```

## 🚧 Known Limitations

- **Simple Intent Recognition**: Uses keyword matching instead of LLM
- **Basic Entity Extraction**: Limited natural language parsing
- **Token Expiration**: Kroger token may expire and need refresh
- **Unit Conversions**: No complex ingredient quantity conversions

## 🤝 Contributing

This is a hackathon project built according to the specifications in `GrocerGenie.md`. Feel free to enhance any of the features or add new functionality!

## 📄 License

This project is for educational and demonstration purposes.