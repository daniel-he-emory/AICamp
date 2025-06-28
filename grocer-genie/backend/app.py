from flask import Flask, request, jsonify, session
from flask_cors import CORS
import json
import os
import requests
from datetime import datetime
import openai
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'grocer-genie-secret-key'
CORS(app)

KROGER_ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsImprdSI6Imh0dHBzOi8vYXBpLmtyb2dlci5jb20vdjEvLndlbGwta25vd24vandrcy5qc29uIiwia2lkIjoiWjRGZDNtc2tJSDg4aXJ0N0xCNWM2Zz09IiwidHlwIjoiSldUIn0.eyJhdWQiOiJhaWNhbXAtYmJjNjc1ZDYiLCJleHAiOjE3NTExNDIyOTUsImlhdCI6MTc1MTE0MDQ5MCwiaXNzIjoiYXBpLmtyb2dlci5jb20iLCJzdWIiOiI1MzgxZDNiMi1mM2JkLTU2NDYtYWI0Zi05YzZmNDUwNjg2NWQiLCJzY29wZSI6InByb2R1Y3QuY29tcGFjdCIsImF1dGhBdCI6MTc1MTE0MDQ5NTQ0MDgyMzk2NCwiYXpwIjoiYWljYW1wLWJiYzY3NWQ2In0.FPrEA7NBTTy_jgLK0xrB-la4hoBUHDO7cmaApJUmtyNSTw1EyiN9T9P8HOFHIE8pqTwTBIKczP4gbnirPe7LcB689CGO68I8TXUP0QTxFQGZNDnAcrUiQKPySo1484OXZO34OtiRN9KXrNfVXUdVQ5-8bxeYmFAZyOMZMrjJ_tCA8lIqUX_3a0DK29Lir2VCROvHqs1KFczq460oQILUtII4XDCSalGpYLY2EU2nNwNzJIV4yr8EjDIlH9gZoPkE4OoQQPNMCWHdNYwWetZ87IFcST7YEOpSu6bZtSMW8I6RSLcWDiegW22RfpcRJzqZ_cSLS2ybZad1iC04Ricm4Q"

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Check if API key is available
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY not found in environment variables.")
    print("Please set your OpenAI API key using one of these methods:")
    print("1. Create a .env file in the backend directory with: OPENAI_API_KEY=your_key_here")
    print("2. Set environment variable: export OPENAI_API_KEY=your_key_here")
    print("3. The app will still work with fallback keyword matching, but AI features will be limited.")

openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionState:
    def __init__(self):
        self.pantry = {}
        self.current_meal_plan = []
        self.current_shopping_list = []
        self.user_preferences = {}
        
    def to_dict(self):
        return {
            'pantry': self.pantry,
            'current_meal_plan': self.current_meal_plan,
            'current_shopping_list': self.current_shopping_list,
            'user_preferences': self.user_preferences
        }
    
    def from_dict(self, data):
        self.pantry = data.get('pantry', {})
        self.current_meal_plan = data.get('current_meal_plan', [])
        self.current_shopping_list = data.get('current_shopping_list', [])
        self.user_preferences = data.get('user_preferences', {})

def get_session_state():
    if 'state' not in session:
        session['state'] = SessionState().to_dict()
    state = SessionState()
    state.from_dict(session['state'])
    return state

def save_session_state(state):
    session['state'] = state.to_dict()

def load_pantry():
    pantry_file = '../data/pantry.json'
    if os.path.exists(pantry_file):
        with open(pantry_file, 'r') as f:
            return json.load(f)
    return {}

def save_pantry(pantry):
    pantry_file = '../data/pantry.json'
    os.makedirs(os.path.dirname(pantry_file), exist_ok=True)
    with open(pantry_file, 'w') as f:
        json.dump(pantry, f, indent=2)

def call_openai_with_fallback(messages, temperature=0.3, max_tokens=500):
    """
    Call OpenAI API with error handling and fallback
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-search-preview",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip(), None
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return None, str(e)

def get_intent_classification_prompt():
    """
    Return the prompt template for intent classification
    """
    return """You are a grocery shopping assistant. Classify the user's message into one of these intents:

- update_pantry: User wants to add, remove, or modify items in their pantry
- check_pantry: User wants to see what's currently in their pantry
- request_meal_plan: User wants recipe suggestions or meal planning
- add_to_cart: User wants to add items to their Kroger shopping cart
- clarification: Message is unclear or doesn't fit other categories

Examples:
"I bought 2 onions and a bag of rice" -> update_pantry
"What's in my pantry?" -> check_pantry
"I want to cook Italian food tonight" -> request_meal_plan
"Add these items to my cart" -> add_to_cart
"Hello" -> clarification

User message: "{message}"

Respond with only the intent name (e.g., "update_pantry")."""

def get_entity_extraction_prompt():
    """
    Return the prompt template for entity extraction
    """
    return """You are a grocery shopping assistant. Extract food items, quantities, and actions from the user's message.

Return a JSON array with objects containing:
- item: the food item name (normalized, lowercase, singular)
- quantity: numeric quantity (use 1 if not specified)
- action: "add" (for buying/adding items) or "remove" (for using up/finishing items)

Examples:
"I bought 2 onions and a bag of rice" -> [{{"item": "onion", "quantity": 2, "action": "add"}}, {{"item": "rice", "quantity": 1, "action": "add"}}]
"I finished the milk and used up 3 eggs" -> [{{"item": "milk", "quantity": 0, "action": "remove"}}, {{"item": "egg", "quantity": 3, "action": "remove"}}]
"I got some chicken and 5 apples" -> [{{"item": "chicken", "quantity": 1, "action": "add"}}, {{"item": "apple", "quantity": 5, "action": "add"}}]

User message: "{message}"

Respond with only valid JSON:"""

def normalize_ingredient_name(name):
    """
    Normalize ingredient names for better matching
    """
    # Convert to lowercase and remove common variations
    name = name.lower().strip()
    
    # Common ingredient variations
    variations = {
        'tomato': ['tomatoes', 'tomato'],
        'onion': ['onions', 'onion'],
        'garlic': ['garlic', 'garlic clove', 'garlic cloves'],
        'egg': ['eggs', 'egg'],
        'milk': ['milk', 'whole milk', 'skim milk'],
        'butter': ['butter', 'unsalted butter', 'salted butter'],
        'olive oil': ['olive oil', 'extra virgin olive oil', 'evoo'],
        'salt': ['salt', 'table salt', 'kosher salt'],
        'pepper': ['pepper', 'black pepper', 'ground pepper'],
        'flour': ['flour', 'all purpose flour', 'plain flour'],
        'sugar': ['sugar', 'white sugar', 'granulated sugar'],
        'rice': ['rice', 'white rice', 'brown rice'],
        'pasta': ['pasta', 'spaghetti', 'penne', 'fettuccine'],
        'chicken': ['chicken', 'chicken breast', 'chicken thighs'],
        'beef': ['beef', 'ground beef', 'beef steak'],
        'cheese': ['cheese', 'cheddar cheese', 'mozzarella cheese']
    }
    
    # Check if the name matches any variation
    for base_name, variants in variations.items():
        if name in variants:
            return base_name
    
    return name

def check_ingredient_availability(ingredient_name, pantry_items):
    """
    Check if an ingredient is available in the pantry, accounting for variations
    """
    normalized_name = normalize_ingredient_name(ingredient_name)
    
    # Check exact match first
    if ingredient_name in pantry_items:
        return True, pantry_items[ingredient_name]
    
    # Check normalized match
    if normalized_name in pantry_items:
        return True, pantry_items[normalized_name]
    
    # Check if any pantry item contains the ingredient name
    for pantry_item, quantity in pantry_items.items():
        if normalized_name in normalize_ingredient_name(pantry_item):
            return True, quantity
    
    return False, 0

def recognize_intent(message):
    """
    LLM-powered intent recognition with fallback to keyword matching
    """
    prompt = get_intent_classification_prompt().format(message=message)
    messages = [{"role": "user", "content": prompt}]
    
    response, error = call_openai_with_fallback(messages, temperature=0.1, max_tokens=50)
    
    if response:
        # Clean response and validate
        intent = response.lower().strip()
        valid_intents = ['update_pantry', 'check_pantry', 'request_meal_plan', 'add_to_cart', 'clarification']
        
        if intent in valid_intents:
            logger.info(f"LLM classified intent: {intent}")
            return intent
        else:
            logger.warning(f"LLM returned invalid intent: {intent}, falling back to keyword matching")
    else:
        logger.warning(f"LLM intent recognition failed: {error}, falling back to keyword matching")
    
    # Fallback to keyword matching
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['pantry', 'have', 'inventory', 'bought', 'finished', 'added', 'removed']):
        if any(word in message_lower for word in ['what', 'show', 'check', 'list']):
            return 'check_pantry'
        return 'update_pantry'
    
    if any(word in message_lower for word in ['recipe', 'meal', 'cook', 'dinner', 'lunch', 'breakfast', 'plan']):
        return 'request_meal_plan'
    
    if any(word in message_lower for word in ['cart', 'buy', 'purchase', 'kroger', 'add to cart']):
        return 'add_to_cart'
    
    return 'clarification'

def extract_pantry_entities(message):
    """
    LLM-powered entity extraction with fallback to simple parsing
    """
    prompt = get_entity_extraction_prompt().format(message=message)
    messages = [{"role": "user", "content": prompt}]
    
    response, error = call_openai_with_fallback(messages, temperature=0.1, max_tokens=300)
    
    if response:
        try:
            # Try to parse JSON response
            entities = json.loads(response)
            
            # Validate structure
            if isinstance(entities, list):
                valid_entities = []
                for entity in entities:
                    if (isinstance(entity, dict) and 
                        'item' in entity and 'quantity' in entity and 'action' in entity and
                        entity['action'] in ['add', 'remove'] and
                        isinstance(entity['quantity'], (int, float))):
                        valid_entities.append(entity)
                
                if valid_entities:
                    logger.info(f"LLM extracted {len(valid_entities)} entities")
                    return valid_entities
                else:
                    logger.warning("LLM returned invalid entity structure, falling back to simple parsing")
            else:
                logger.warning("LLM response is not a list, falling back to simple parsing")
        except json.JSONDecodeError as e:
            logger.warning(f"LLM returned invalid JSON: {e}, falling back to simple parsing")
    else:
        logger.warning(f"LLM entity extraction failed: {error}, falling back to simple parsing")
    
    # Fallback to simple parsing
    entities = []
    
    # Simple patterns for demo
    if 'bought' in message.lower() or 'added' in message.lower():
        # Extract items after "bought" or "added"
        words = message.lower().split()
        for i, word in enumerate(words):
            if word in ['bought', 'added'] and i + 1 < len(words):
                # Simple extraction - look for numbers and items
                if words[i + 1].isdigit():
                    quantity = int(words[i + 1])
                    if i + 2 < len(words):
                        item = words[i + 2].rstrip('.,')
                        entities.append({"item": item, "quantity": quantity, "action": "add"})
    
    if 'finished' in message.lower() or 'removed' in message.lower():
        words = message.lower().split()
        for i, word in enumerate(words):
            if word in ['finished', 'removed'] and i + 1 < len(words):
                item = words[i + 1].rstrip('.,')
                entities.append({"item": item, "quantity": 0, "action": "remove"})
    
    return entities

def fetch_recipes(cuisine=None, dietary_restrictions=None, num_meals=3):
    """
    Fetch recipes from TheMealDB API
    """
    base_url = "https://www.themealdb.com/api/json/v1/1"
    
    if cuisine:
        url = f"{base_url}/filter.php?a={cuisine}"
    else:
        url = f"{base_url}/search.php?s="
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get('meals'):
            meals = data['meals'][:num_meals]
            recipes = []
            
            for meal in meals:
                recipe = {
                    'id': meal['idMeal'],
                    'name': meal['strMeal'],
                    'image': meal['strMealThumb'],
                    'ingredients': []
                }
                
                # Extract ingredients and measures
                for i in range(1, 21):  # TheMealDB has up to 20 ingredients
                    ingredient = meal.get(f'strIngredient{i}')
                    measure = meal.get(f'strMeasure{i}')
                    
                    if ingredient and ingredient.strip():
                        recipe['ingredients'].append({
                            'name': ingredient.strip(),
                            'measure': measure.strip() if measure else ''
                        })
                
                recipes.append(recipe)
            
            return recipes
        else:
            return []
    except Exception as e:
        print(f"Error fetching recipes: {e}")
        return []

def create_shopping_list(meal_plan, pantry):
    """
    Compare meal plan ingredients with pantry to create shopping list
    """
    shopping_list = []
    required_ingredients = {}
    
    # Aggregate all ingredients from meal plan
    for recipe in meal_plan:
        for ingredient in recipe['ingredients']:
            name = ingredient['name'].lower()
            if name in required_ingredients:
                required_ingredients[name] += 1
            else:
                required_ingredients[name] = 1
    
    # Check against pantry
    for ingredient, needed_quantity in required_ingredients.items():
        pantry_quantity = pantry.get(ingredient, 0)
        
        if pantry_quantity < needed_quantity:
            shopping_list.append({
                'name': ingredient,
                'needed': needed_quantity - pantry_quantity
            })
    
    return shopping_list

def search_kroger_products(product_name, zip_code=None):
    """
    Search for products in Kroger using their API
    """
    headers = {
        'Authorization': f'Bearer {KROGER_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Find location first if zip_code is provided
    location_id = None
    if zip_code:
        location_id = find_kroger_location(zip_code)
    
    # Search for products
    params = {
        'filter.term': product_name,
        'filter.limit': 5
    }
    
    if location_id:
        params['filter.locationId'] = location_id
    
    try:
        response = requests.get(
            'https://api.kroger.com/v1/products',
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        else:
            print(f"Kroger API error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Error searching Kroger products: {e}")
        return []

def find_kroger_location(zip_code):
    """
    Find the nearest Kroger location by zip code
    """
    headers = {
        'Authorization': f'Bearer {KROGER_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'filter.zipCode.near': zip_code,
        'filter.limit': 1
    }
    
    try:
        response = requests.get(
            'https://api.kroger.com/v1/locations',
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            locations = data.get('data', [])
            if locations:
                return locations[0]['locationId']
        else:
            print(f"Kroger location API error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error finding Kroger location: {e}")
    
    return None

def add_items_to_kroger_cart(product_ids):
    """
    Add multiple items to Kroger cart
    """
    headers = {
        'Authorization': f'Bearer {KROGER_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Prepare items for bulk add
    items = []
    for product_id in product_ids:
        items.append({
            'upc': product_id,
            'quantity': 1
        })
    
    payload = {
        'items': items
    }
    
    try:
        response = requests.put(
            'https://api.kroger.com/v1/cart/add',
            headers=headers,
            json=payload
        )
        
        if response.status_code in [200, 204]:
            return True, "Items successfully added to cart"
        else:
            print(f"Kroger cart API error: {response.status_code} - {response.text}")
            return False, f"Failed to add items to cart: {response.status_code}"
    except Exception as e:
        print(f"Error adding items to Kroger cart: {e}")
        return False, f"Error adding items to cart: {str(e)}"

def get_recipe_selection_prompt(pantry_items, cuisine=None):
    """
    Return the prompt template for LLM-powered recipe selection based on pantry
    """
    pantry_text = ", ".join([f"{item} ({quantity})" for item, quantity in pantry_items.items()]) if pantry_items else "empty pantry"
    
    cuisine_filter = f" Focus on {cuisine} cuisine." if cuisine else ""
    
    return f"""You are a smart recipe recommendation system. Based on the user's pantry ingredients, suggest 3 recipes they can make.

User's pantry: {pantry_text}
{cuisine_filter}

Rules:
1. Only suggest recipes where the user has MOST of the required ingredients (at least 60% of ingredients)
2. If the user has very few ingredients, suggest simple recipes with minimal ingredients
3. For missing ingredients, suggest common substitutions or note they need to buy them
4. Prioritize recipes that use the most pantry ingredients
5. Be realistic about what can be made with the available ingredients
6. Consider ingredient variations (e.g., "eggs" vs "egg", "tomatoes" vs "tomato")

For each recipe, provide:
- Recipe name
- List of ingredients (mark which ones the user has with "has": true and which they need to buy with "has": false)
- Brief cooking instructions
- Estimated cooking time

Respond in this JSON format:
{{
  "recipes": [
    {{
      "name": "Recipe Name",
      "ingredients": [
        {{"name": "ingredient name", "has": true/false, "substitution": "optional substitution"}}
      ],
      "instructions": "Brief cooking steps",
      "cooking_time": "30 minutes"
    }}
  ]
}}

IMPORTANT: Only include ingredients that are actually needed for the recipe. Don't add unnecessary ingredients. Be precise about what the user has vs what they need to buy.

User message: "I want to cook something with what I have" """

def select_recipes_with_llm(pantry_items, cuisine=None):
    """
    Use LLM to intelligently select recipes based on available pantry ingredients
    """
    if not pantry_items:
        # If pantry is empty, return simple recipes that require minimal ingredients
        return [{
            "name": "Simple Pasta with Olive Oil",
            "ingredients": [
                {"name": "pasta", "has": False, "substitution": None},
                {"name": "olive oil", "has": False, "substitution": None},
                {"name": "salt", "has": False, "substitution": None}
            ],
            "instructions": "Boil pasta according to package instructions. Drain and toss with olive oil and salt.",
            "cooking_time": "15 minutes"
        }]
    
    prompt = get_recipe_selection_prompt(pantry_items, cuisine)
    messages = [{"role": "user", "content": prompt}]
    
    response, error = call_openai_with_fallback(messages, temperature=0.3, max_tokens=800)
    
    if response:
        try:
            # Try to parse JSON response
            recipe_data = json.loads(response)
            
            if isinstance(recipe_data, dict) and 'recipes' in recipe_data:
                recipes = recipe_data['recipes']
                if isinstance(recipes, list) and len(recipes) > 0:
                    logger.info(f"LLM selected {len(recipes)} recipes based on pantry")
                    return recipes
                else:
                    logger.warning("LLM returned empty recipes list, falling back to simple recipes")
            else:
                logger.warning("LLM response missing 'recipes' key, falling back to simple recipes")
        except json.JSONDecodeError as e:
            logger.warning(f"LLM returned invalid JSON: {e}, falling back to simple recipes")
    else:
        logger.warning(f"LLM recipe selection failed: {error}, falling back to simple recipes")
    
    # Fallback to simple recipe suggestions based on available ingredients
    return create_fallback_recipes(pantry_items, cuisine)

def create_fallback_recipes(pantry_items, cuisine=None):
    """
    Create simple fallback recipes when LLM fails
    """
    recipes = []
    
    # Simple recipe templates based on common ingredients
    has_eggs, egg_quantity = check_ingredient_availability('eggs', pantry_items)
    if has_eggs:
        has_butter, _ = check_ingredient_availability('butter', pantry_items)
        has_salt, _ = check_ingredient_availability('salt', pantry_items)
        
        recipes.append({
            "name": "Scrambled Eggs",
            "ingredients": [
                {"name": "eggs", "has": True, "substitution": None},
                {"name": "butter", "has": has_butter, "substitution": "oil" if not has_butter else None},
                {"name": "salt", "has": has_salt, "substitution": None}
            ],
            "instructions": "Crack eggs into bowl, whisk. Heat pan with butter/oil, add eggs and scramble until cooked.",
            "cooking_time": "5 minutes"
        })
    
    has_pasta, _ = check_ingredient_availability('pasta', pantry_items)
    if has_pasta:
        has_oil, _ = check_ingredient_availability('olive oil', pantry_items)
        has_salt, _ = check_ingredient_availability('salt', pantry_items)
        
        recipes.append({
            "name": "Simple Pasta",
            "ingredients": [
                {"name": "pasta", "has": True, "substitution": None},
                {"name": "olive oil", "has": has_oil, "substitution": "butter" if not has_oil else None},
                {"name": "salt", "has": has_salt, "substitution": None}
            ],
            "instructions": "Boil pasta in salted water until al dente. Drain and toss with oil/butter.",
            "cooking_time": "15 minutes"
        })
    
    has_rice, _ = check_ingredient_availability('rice', pantry_items)
    if has_rice:
        has_salt, _ = check_ingredient_availability('salt', pantry_items)
        
        recipes.append({
            "name": "Simple Rice",
            "ingredients": [
                {"name": "rice", "has": True, "substitution": None},
                {"name": "water", "has": True, "substitution": None},
                {"name": "salt", "has": has_salt, "substitution": None}
            ],
            "instructions": "Rinse rice, add to pot with water (2:1 ratio). Bring to boil, reduce heat, cover and simmer 20 minutes.",
            "cooking_time": "25 minutes"
        })
    
    # If no specific ingredients match, suggest a basic shopping list
    if not recipes:
        recipes.append({
            "name": "Basic Grocery Shopping",
            "ingredients": [
                {"name": "pasta", "has": False, "substitution": None},
                {"name": "eggs", "has": False, "substitution": None},
                {"name": "bread", "has": False, "substitution": None},
                {"name": "milk", "has": False, "substitution": None}
            ],
            "instructions": "These are basic ingredients to get started. Add them to your cart and I can suggest recipes!",
            "cooking_time": "Shopping trip"
        })
    
    return recipes[:3]  # Return max 3 recipes

@app.route('/chat-with-agent', methods=['POST'])
def chat_with_agent():
    data = request.json
    message = data.get('message', '')
    
    state = get_session_state()
    
    # Load pantry from file
    state.pantry = load_pantry()
    
    # Recognize intent
    intent = recognize_intent(message)
    
    response = {'type': 'text', 'message': ''}
    
    if intent == 'check_pantry':
        if state.pantry:
            pantry_items = [f"{item}: {quantity}" for item, quantity in state.pantry.items()]
            response['message'] = f"Your pantry contains: {', '.join(pantry_items)}"
        else:
            response['message'] = "Your pantry is empty. You can add items by telling me what you bought or have."
    
    elif intent == 'update_pantry':
        entities = extract_pantry_entities(message)
        
        if entities:
            for entity in entities:
                item = entity['item']
                quantity = entity['quantity']
                action = entity['action']
                
                if action == 'add':
                    state.pantry[item] = state.pantry.get(item, 0) + quantity
                elif action == 'remove':
                    if item in state.pantry:
                        del state.pantry[item]
            
            save_pantry(state.pantry)
            response['message'] = "I've updated your pantry!"
        else:
            response['message'] = "I couldn't understand what items you want to update. Please try again."
    
    elif intent == 'request_meal_plan':
        # Extract cuisine or dietary preferences
        cuisine = None
        if 'italian' in message.lower():
            cuisine = 'Italian'
        elif 'mexican' in message.lower():
            cuisine = 'Mexican'
        elif 'chinese' in message.lower():
            cuisine = 'Chinese'
        
        # Use LLM to select recipes based on pantry contents
        recipes = select_recipes_with_llm(state.pantry, cuisine)
        
        if recipes:
            state.current_meal_plan = recipes
            
            # Create shopping list from missing ingredients
            shopping_list = []
            for recipe in recipes:
                for ingredient in recipe['ingredients']:
                    if not ingredient['has']:
                        # Check if we already have this item in shopping list
                        existing_item = next((item for item in shopping_list if item['name'] == ingredient['name']), None)
                        if existing_item:
                            existing_item['needed'] += 1
                        else:
                            shopping_list.append({
                                'name': ingredient['name'],
                                'needed': 1
                            })
            
            state.current_shopping_list = shopping_list
            
            response = {
                'type': 'meal_plan',
                'meal_plan': recipes,
                'shopping_list': shopping_list,
                'message': f"Here's your personalized meal plan with {len(recipes)} recipes based on your pantry!"
            }
        else:
            response['message'] = "Sorry, I couldn't find any recipes. Please try again."
    
    elif intent == 'add_to_cart':
        if not state.user_preferences.get('zip_code'):
            # Check if message contains a zip code
            import re
            zip_match = re.search(r'\b\d{5}\b', message)
            if zip_match:
                zip_code = zip_match.group()
                state.user_preferences['zip_code'] = zip_code
                response['message'] = f"Got it! I've set your zip code to {zip_code}. Now let me add your items to the Kroger cart..."
                # Continue with cart logic below
            else:
                response['message'] = "I need your zip code to find a nearby Kroger store. What is your zip code?"
                save_session_state(state)
                return jsonify(response)
        
        if not state.current_shopping_list:
            response['message'] = "You don't have any items in your shopping list. Please create a meal plan first."
        else:
            # Implement the agentic workflow for adding items to cart
            product_ids = []
            not_found_items = []
            
            for item in state.current_shopping_list:
                # Search for each item in Kroger
                products = search_kroger_products(item['name'], state.user_preferences.get('zip_code'))
                
                if products:
                    # Select the first product (as per MVP requirements)
                    product_id = products[0].get('productId')
                    if product_id:
                        product_ids.append(product_id)
                    else:
                        not_found_items.append(item['name'])
                else:
                    not_found_items.append(item['name'])
            
            # Add found items to cart
            if product_ids:
                success, message = add_items_to_kroger_cart(product_ids)
                
                if success:
                    success_count = len(product_ids)
                    response_message = f"I've added {success_count} items to your Kroger cart!"
                    
                    if not_found_items:
                        response_message += f" I couldn't find these items: {', '.join(not_found_items)}"
                    
                    response['message'] = response_message
                else:
                    response['message'] = f"Sorry, I had trouble adding items to your cart: {message}"
            else:
                response['message'] = f"I couldn't find any of the items in your shopping list at Kroger: {', '.join(not_found_items)}"
    
    else:
        response['message'] = "I'm not sure what you want to do. You can ask me to check your pantry, update your pantry, create a meal plan, or add items to your Kroger cart."
    
    save_session_state(state)
    
    return jsonify(response)

@app.route('/set-zipcode', methods=['POST'])
def set_zipcode():
    data = request.json
    zipcode = data.get('zipcode', '')
    
    state = get_session_state()
    state.user_preferences['zip_code'] = zipcode
    save_session_state(state)
    
    return jsonify({'message': f'Zip code set to {zipcode}'})

if __name__ == '__main__':
    app.run(debug=True, port=5001)