from flask import Flask, request, jsonify, session
from flask_cors import CORS
import json
import os
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'grocer-genie-secret-key'
CORS(app)

KROGER_ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsImprdSI6Imh0dHBzOi8vYXBpLmtyb2dlci5jb20vdjEvLndlbGwta25vd24vandrcy5qc29uIiwia2lkIjoiWjRGZDNtc2tJSDg4aXJ0N0xCNWM2Zz09IiwidHlwIjoiSldUIn0.eyJhdWQiOiJhaWNhbXAtYmJjNjc1ZDYiLCJleHAiOjE3NTExNDIyOTUsImlhdCI6MTc1MTE0MDQ5MCwiaXNzIjoiYXBpLmtyb2dlci5jb20iLCJzdWIiOiI1MzgxZDNiMi1mM2JkLTU2NDYtYWI0Zi05YzZmNDUwNjg2NWQiLCJzY29wZSI6InByb2R1Y3QuY29tcGFjdCIsImF1dGhBdCI6MTc1MTE0MDQ5NTQ0MDgyMzk2NCwiYXpwIjoiYWljYW1wLWJiYzY3NWQ2In0.FPrEA7NBTTy_jgLK0xrB-la4hoBUHDO7cmaApJUmtyNSTw1EyiN9T9P8HOFHIE8pqTwTBIKczP4gbnirPe7LcB689CGO68I8TXUP0QTxFQGZNDnAcrUiQKPySo1484OXZO34OtiRN9KXrNfVXUdVQ5-8bxeYmFAZyOMZMrjJ_tCA8lIqUX_3a0DK29Lir2VCROvHqs1KFczq460oQILUtII4XDCSalGpYLY2EU2nNwNzJIV4yr8EjDIlH9gZoPkE4OoQQPNMCWHdNYwWetZ87IFcST7YEOpSu6bZtSMW8I6RSLcWDiegW22RfpcRJzqZ_cSLS2ybZad1iC04Ricm4Q"

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

def recognize_intent(message):
    """
    Simple intent recognition - in a real app, this would use an LLM
    For now, using keyword matching
    """
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
    Simple entity extraction - in a real app, this would use an LLM
    For now, using simple parsing
    """
    # This is a simplified version - in reality, you'd use an LLM for better parsing
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
        
        recipes = fetch_recipes(cuisine=cuisine)
        
        if recipes:
            state.current_meal_plan = recipes
            shopping_list = create_shopping_list(recipes, state.pantry)
            state.current_shopping_list = shopping_list
            
            response = {
                'type': 'meal_plan',
                'meal_plan': recipes,
                'shopping_list': shopping_list,
                'message': f"Here's your meal plan with {len(recipes)} recipes!"
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
    app.run(debug=True, port=5000)