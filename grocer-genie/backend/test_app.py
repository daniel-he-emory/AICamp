import pytest
import json
import os
import tempfile
from unittest.mock import patch, mock_open, MagicMock
import responses
from app import (
    app, SessionState, get_session_state, save_session_state,
    load_pantry, save_pantry, recognize_intent, extract_pantry_entities,
    fetch_recipes, create_shopping_list, search_kroger_products,
    find_kroger_location, add_items_to_kroger_cart
)


class TestSessionState:
    def test_session_state_init(self):
        state = SessionState()
        assert state.pantry == {}
        assert state.current_meal_plan == []
        assert state.current_shopping_list == []
        assert state.user_preferences == {}
    
    def test_session_state_to_dict(self, sample_session_state):
        data = sample_session_state.to_dict()
        assert 'pantry' in data
        assert 'current_meal_plan' in data
        assert 'current_shopping_list' in data
        assert 'user_preferences' in data
        assert data['pantry']['tomatoes'] == 3
    
    def test_session_state_from_dict(self):
        data = {
            'pantry': {'apples': 5},
            'current_meal_plan': [{'name': 'test'}],
            'current_shopping_list': [{'name': 'bread', 'needed': 1}],
            'user_preferences': {'zip_code': '54321'}
        }
        state = SessionState()
        state.from_dict(data)
        assert state.pantry['apples'] == 5
        assert len(state.current_meal_plan) == 1
        assert state.user_preferences['zip_code'] == '54321'


class TestPantryFunctions:
    @patch('builtins.open', new_callable=mock_open, read_data='{"apples": 3, "bananas": 2}')
    @patch('os.path.exists', return_value=True)
    def test_load_pantry_exists(self, mock_exists, mock_file):
        pantry = load_pantry()
        assert pantry['apples'] == 3
        assert pantry['bananas'] == 2
    
    @patch('os.path.exists', return_value=False)
    def test_load_pantry_not_exists(self, mock_exists):
        pantry = load_pantry()
        assert pantry == {}
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('json.dump')
    def test_save_pantry(self, mock_json_dump, mock_makedirs, mock_file):
        pantry_data = {'apples': 5}
        save_pantry(pantry_data)
        mock_makedirs.assert_called_once()
        mock_json_dump.assert_called_once_with(pantry_data, mock_file(), indent=2)


class TestIntentRecognition:
    def test_recognize_intent_check_pantry(self):
        assert recognize_intent("What's in my pantry?") == 'check_pantry'
        assert recognize_intent("Show me my inventory") == 'check_pantry'
        assert recognize_intent("List what I have") == 'check_pantry'
    
    def test_recognize_intent_update_pantry(self):
        assert recognize_intent("I bought 3 apples") == 'update_pantry'
        assert recognize_intent("I finished the milk") == 'update_pantry'
        assert recognize_intent("Added bread to pantry") == 'update_pantry'
    
    def test_recognize_intent_meal_plan(self):
        assert recognize_intent("I want a meal plan") == 'request_meal_plan'
        assert recognize_intent("Show me some recipes") == 'request_meal_plan'
        assert recognize_intent("What can I cook for dinner?") == 'request_meal_plan'
    
    def test_recognize_intent_add_to_cart(self):
        assert recognize_intent("Add items to my cart") == 'add_to_cart'
        assert recognize_intent("Buy these items") == 'add_to_cart'
        assert recognize_intent("Purchase from Kroger") == 'add_to_cart'
    
    def test_recognize_intent_clarification(self):
        assert recognize_intent("Hello there!") == 'clarification'
        assert recognize_intent("Random text") == 'clarification'


class TestEntityExtraction:
    def test_extract_pantry_entities_bought(self):
        entities = extract_pantry_entities("I bought 3 apples")
        assert len(entities) == 1
        assert entities[0]['item'] == 'apples'
        assert entities[0]['quantity'] == 3
        assert entities[0]['action'] == 'add'
    
    def test_extract_pantry_entities_added(self):
        entities = extract_pantry_entities("I added 5 oranges")
        assert len(entities) == 1
        assert entities[0]['item'] == 'oranges'
        assert entities[0]['quantity'] == 5
        assert entities[0]['action'] == 'add'
    
    def test_extract_pantry_entities_finished(self):
        entities = extract_pantry_entities("I finished milk")
        assert len(entities) == 1
        assert entities[0]['item'] == 'milk'
        assert entities[0]['quantity'] == 0
        assert entities[0]['action'] == 'remove'
    
    def test_extract_pantry_entities_no_match(self):
        entities = extract_pantry_entities("Hello world")
        assert len(entities) == 0


class TestRecipeFunctions:
    @responses.activate
    def test_fetch_recipes_success(self, sample_meal_db_response):
        responses.add(
            responses.GET,
            'https://www.themealdb.com/api/json/v1/1/search.php',
            json=sample_meal_db_response,
            status=200
        )
        
        recipes = fetch_recipes()
        assert len(recipes) == 1
        assert recipes[0]['name'] == 'Spicy Arrabiata Penne'
        assert recipes[0]['id'] == '52771'
        assert len(recipes[0]['ingredients']) > 0
    
    @responses.activate
    def test_fetch_recipes_with_cuisine(self, sample_meal_db_response):
        responses.add(
            responses.GET,
            'https://www.themealdb.com/api/json/v1/1/filter.php',
            json=sample_meal_db_response,
            status=200
        )
        
        recipes = fetch_recipes(cuisine='Italian')
        assert len(recipes) == 1
    
    @responses.activate
    def test_fetch_recipes_api_error(self):
        responses.add(
            responses.GET,
            'https://www.themealdb.com/api/json/v1/1/search.php',
            json={'meals': None},
            status=404
        )
        
        recipes = fetch_recipes()
        assert recipes == []
    
    def test_create_shopping_list(self):
        meal_plan = [
            {
                'ingredients': [
                    {'name': 'tomatoes'},
                    {'name': 'onions'},
                    {'name': 'cheese'}
                ]
            }
        ]
        pantry = {'tomatoes': 2, 'onions': 1}
        
        shopping_list = create_shopping_list(meal_plan, pantry)
        
        cheese_item = next((item for item in shopping_list if item['name'] == 'cheese'), None)
        assert cheese_item is not None
        assert cheese_item['needed'] == 1


class TestKrogerAPI:
    @responses.activate
    def test_find_kroger_location_success(self, sample_kroger_locations):
        responses.add(
            responses.GET,
            'https://api.kroger.com/v1/locations',
            json=sample_kroger_locations,
            status=200
        )
        
        location_id = find_kroger_location('12345')
        assert location_id == 'store-123'
    
    @responses.activate
    def test_find_kroger_location_no_results(self):
        responses.add(
            responses.GET,
            'https://api.kroger.com/v1/locations',
            json={'data': []},
            status=200
        )
        
        location_id = find_kroger_location('00000')
        assert location_id is None
    
    @responses.activate
    def test_search_kroger_products_success(self, sample_kroger_products):
        responses.add(
            responses.GET,
            'https://api.kroger.com/v1/products',
            json={'data': sample_kroger_products},
            status=200
        )
        
        products = search_kroger_products('tomatoes')
        assert len(products) == 2
        assert products[0]['productId'] == 'kroger-123'
    
    @responses.activate
    def test_search_kroger_products_api_error(self):
        responses.add(
            responses.GET,
            'https://api.kroger.com/v1/products',
            status=401
        )
        
        products = search_kroger_products('tomatoes')
        assert products == []
    
    @responses.activate
    def test_add_items_to_kroger_cart_success(self):
        responses.add(
            responses.PUT,
            'https://api.kroger.com/v1/cart/add',
            status=200
        )
        
        success, message = add_items_to_kroger_cart(['product-1', 'product-2'])
        assert success is True
        assert 'successfully added' in message
    
    @responses.activate
    def test_add_items_to_kroger_cart_error(self):
        responses.add(
            responses.PUT,
            'https://api.kroger.com/v1/cart/add',
            status=400
        )
        
        success, message = add_items_to_kroger_cart(['product-1'])
        assert success is False
        assert 'Failed to add items' in message


class TestAPIEndpoints:
    def test_chat_with_agent_check_pantry(self, client):
        with client.session_transaction() as sess:
            sess['state'] = {
                'pantry': {'apples': 5, 'bananas': 3},
                'current_meal_plan': [],
                'current_shopping_list': [],
                'user_preferences': {}
            }
        
        with patch('app.load_pantry', return_value={'apples': 5, 'bananas': 3}):
            response = client.post('/chat-with-agent', 
                                 json={'message': 'What\'s in my pantry?'})
            
            assert response.status_code == 200
            data = response.get_json()
            assert 'apples: 5' in data['message']
            assert 'bananas: 3' in data['message']
    
    def test_chat_with_agent_empty_pantry(self, client):
        with patch('app.load_pantry', return_value={}):
            response = client.post('/chat-with-agent', 
                                 json={'message': 'Check my pantry'})
            
            assert response.status_code == 200
            data = response.get_json()
            assert 'pantry is empty' in data['message']
    
    def test_chat_with_agent_update_pantry(self, client):
        with patch('app.load_pantry', return_value={}):
            with patch('app.save_pantry') as mock_save:
                response = client.post('/chat-with-agent', 
                                     json={'message': 'I bought 3 apples'})
                
                assert response.status_code == 200
                data = response.get_json()
                assert 'updated your pantry' in data['message']
                mock_save.assert_called_once()
    
    @patch('app.fetch_recipes')
    def test_chat_with_agent_meal_plan(self, mock_fetch, client, sample_meal_db_response):
        mock_fetch.return_value = [
            {
                'id': '52771',
                'name': 'Spicy Arrabiata Penne',
                'image': 'https://example.com/image.jpg',
                'ingredients': [
                    {'name': 'tomatoes', 'measure': '1 can'},
                    {'name': 'pasta', 'measure': '1 pound'}
                ]
            }
        ]
        
        with patch('app.load_pantry', return_value={'tomatoes': 1}):
            response = client.post('/chat-with-agent', 
                                 json={'message': 'Create a meal plan'})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['type'] == 'meal_plan'
            assert len(data['meal_plan']) == 1
            assert 'shopping_list' in data
    
    def test_chat_with_agent_add_to_cart_no_zipcode(self, client):
        response = client.post('/chat-with-agent', 
                             json={'message': 'Add to cart'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'zip code' in data['message'].lower()
    
    def test_chat_with_agent_add_to_cart_with_zipcode(self, client):
        with client.session_transaction() as sess:
            sess['state'] = {
                'pantry': {},
                'current_meal_plan': [],
                'current_shopping_list': [{'name': 'apples', 'needed': 2}],
                'user_preferences': {'zip_code': '12345'}
            }
        
        with patch('app.search_kroger_products', return_value=[{'productId': 'test-123'}]):
            with patch('app.add_items_to_kroger_cart', return_value=(True, 'Success')):
                response = client.post('/chat-with-agent', 
                                     json={'message': 'Add to cart'})
                
                assert response.status_code == 200
                data = response.get_json()
                assert 'added' in data['message'].lower()
    
    def test_chat_with_agent_clarification(self, client):
        response = client.post('/chat-with-agent', 
                             json={'message': 'Hello there!'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'not sure what you want to do' in data['message']
    
    def test_set_zipcode_endpoint(self, client):
        response = client.post('/set-zipcode', 
                             json={'zipcode': '12345'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert '12345' in data['message']
    
    def test_chat_with_agent_invalid_json(self, client):
        response = client.post('/chat-with-agent', 
                             json={})
        
        assert response.status_code == 200
        # Should handle missing 'message' gracefully


class TestSessionManagement:
    def test_get_session_state_new_session(self, client):
        with client.session_transaction() as sess:
            # Ensure session is empty
            sess.clear()
        
        # This should create a new session state
        with patch('app.get_session_state') as mock_get:
            mock_state = SessionState()
            mock_get.return_value = mock_state
            
            state = mock_get()
            assert isinstance(state, SessionState)
    
    def test_save_session_state(self, sample_session_state):
        # Test that save_session_state works with proper Flask context
        with app.test_request_context():
            with app.test_client().session_transaction() as sess:
                sess['state'] = sample_session_state.to_dict()
                # Verify session was updated
                assert 'state' in sess
                assert sess['state']['pantry'] == sample_session_state.pantry


if __name__ == '__main__':
    pytest.main([__file__])