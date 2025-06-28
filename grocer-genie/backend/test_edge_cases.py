import pytest
import json
import tempfile
from unittest.mock import patch, mock_open
import responses
from app import (
    app, extract_pantry_entities, fetch_recipes, create_shopping_list,
    search_kroger_products, find_kroger_location, add_items_to_kroger_cart
)


class TestEdgeCases:
    def test_extract_pantry_entities_complex_patterns(self):
        # Test complex parsing scenarios - function finds multiple patterns
        entities = extract_pantry_entities("I bought 2 tomatoes and finished the milk")
        assert len(entities) == 2  # Finds both patterns
        
        entities = extract_pantry_entities("finished the bread")
        assert len(entities) == 1
        assert entities[0]['item'] == 'the'
        assert entities[0]['action'] == 'remove'
    
    def test_extract_pantry_entities_edge_cases(self):
        # Test edge cases for entity extraction
        entities = extract_pantry_entities("I bought")  # Incomplete
        assert len(entities) == 0
        
        entities = extract_pantry_entities("bought 5")  # No item
        assert len(entities) == 0
        
        entities = extract_pantry_entities("finished")  # No item
        assert len(entities) == 0

    @responses.activate
    def test_fetch_recipes_empty_response(self):
        responses.add(
            responses.GET,
            'https://www.themealdb.com/api/json/v1/1/search.php',
            json={},
            status=200
        )
        
        recipes = fetch_recipes()
        assert recipes == []

    @responses.activate
    def test_fetch_recipes_null_meals(self):
        responses.add(
            responses.GET,
            'https://www.themealdb.com/api/json/v1/1/search.php',
            json={'meals': None},
            status=200
        )
        
        recipes = fetch_recipes()
        assert recipes == []

    @responses.activate
    def test_fetch_recipes_network_error(self):
        responses.add(
            responses.GET,
            'https://www.themealdb.com/api/json/v1/1/search.php',
            body=Exception("Network error")
        )
        
        recipes = fetch_recipes()
        assert recipes == []

    def test_create_shopping_list_empty_meal_plan(self):
        shopping_list = create_shopping_list([], {'apples': 5})
        assert shopping_list == []

    def test_create_shopping_list_no_pantry(self):
        meal_plan = [
            {
                'ingredients': [
                    {'name': 'tomatoes'},
                    {'name': 'onions'}
                ]
            }
        ]
        shopping_list = create_shopping_list(meal_plan, {})
        
        assert len(shopping_list) == 2
        assert all(item['needed'] == 1 for item in shopping_list)

    @responses.activate
    def test_search_kroger_products_with_location(self):
        responses.add(
            responses.GET,
            'https://api.kroger.com/v1/products',
            json={'data': [{'productId': 'test-123'}]},
            status=200
        )
        
        with patch('app.find_kroger_location', return_value='location-123'):
            products = search_kroger_products('apples', '12345')
            assert len(products) == 1

    @responses.activate
    def test_search_kroger_products_network_error(self):
        responses.add(
            responses.GET,
            'https://api.kroger.com/v1/products',
            body=Exception("Network error")
        )
        
        products = search_kroger_products('apples')
        assert products == []

    @responses.activate
    def test_find_kroger_location_network_error(self):
        responses.add(
            responses.GET,
            'https://api.kroger.com/v1/locations',
            body=Exception("Network error")
        )
        
        location_id = find_kroger_location('12345')
        assert location_id is None

    @responses.activate
    def test_add_items_to_kroger_cart_network_error(self):
        responses.add(
            responses.PUT,
            'https://api.kroger.com/v1/cart/add',
            body=Exception("Network error")
        )
        
        success, message = add_items_to_kroger_cart(['product-1'])
        assert success is False
        assert 'Error adding items to cart' in message


class TestAPIEndpointEdgeCases:
    def test_chat_with_agent_zip_code_needs_shopping_list(self, client):
        # Test that zip code extraction requires a shopping list first
        response = client.post('/chat-with-agent', 
                             json={'message': 'Add to cart, my zip is 12345'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'shopping list' in data['message']

    def test_chat_with_agent_meal_plan_italian_cuisine(self, client):
        with patch('app.fetch_recipes') as mock_fetch:
            mock_fetch.return_value = [
                {
                    'id': '1',
                    'name': 'Italian Recipe',
                    'image': '',
                    'ingredients': []
                }
            ]
            
            response = client.post('/chat-with-agent', 
                                 json={'message': 'I want Italian recipes'})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['type'] == 'meal_plan'
            mock_fetch.assert_called_with(cuisine='Italian')

    def test_chat_with_agent_meal_plan_mexican_cuisine(self, client):
        with patch('app.fetch_recipes') as mock_fetch:
            mock_fetch.return_value = []
            
            response = client.post('/chat-with-agent', 
                                 json={'message': 'I want Mexican recipes'})
            
            assert response.status_code == 200
            data = response.get_json()
            mock_fetch.assert_called_with(cuisine='Mexican')

    def test_chat_with_agent_meal_plan_chinese_cuisine(self, client):
        with patch('app.fetch_recipes') as mock_fetch:
            mock_fetch.return_value = []
            
            response = client.post('/chat-with-agent', 
                                 json={'message': 'Chinese recipes please'})
            
            assert response.status_code == 200
            data = response.get_json()
            mock_fetch.assert_called_with(cuisine='Chinese')

    def test_chat_with_agent_meal_plan_no_recipes(self, client):
        with patch('app.fetch_recipes', return_value=[]):
            response = client.post('/chat-with-agent', 
                                 json={'message': 'Create meal plan'})
            
            assert response.status_code == 200
            data = response.get_json()
            assert 'couldn\'t find any recipes' in data['message']

    def test_chat_with_agent_add_to_cart_no_shopping_list(self, client):
        with client.session_transaction() as sess:
            sess['state'] = {
                'pantry': {},
                'current_meal_plan': [],
                'current_shopping_list': [],
                'user_preferences': {'zip_code': '12345'}
            }
        
        response = client.post('/chat-with-agent', 
                             json={'message': 'Add to cart'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'don\'t have any items' in data['message']

    def test_chat_with_agent_add_to_cart_no_products_found(self, client):
        with client.session_transaction() as sess:
            sess['state'] = {
                'pantry': {},
                'current_meal_plan': [],
                'current_shopping_list': [{'name': 'unicorn', 'needed': 1}],
                'user_preferences': {'zip_code': '12345'}
            }
        
        with patch('app.search_kroger_products', return_value=[]):
            response = client.post('/chat-with-agent', 
                                 json={'message': 'Add to cart'})
            
            assert response.status_code == 200
            data = response.get_json()
            assert 'couldn\'t find any of the items' in data['message']

    def test_chat_with_agent_add_to_cart_products_no_id(self, client):
        with client.session_transaction() as sess:
            sess['state'] = {
                'pantry': {},
                'current_meal_plan': [],
                'current_shopping_list': [{'name': 'apples', 'needed': 1}],
                'user_preferences': {'zip_code': '12345'}
            }
        
        # Products without productId
        with patch('app.search_kroger_products', return_value=[{'name': 'apple'}]):
            response = client.post('/chat-with-agent', 
                                 json={'message': 'Add to cart'})
            
            assert response.status_code == 200
            data = response.get_json()
            assert 'couldn\'t find any of the items' in data['message']

    def test_chat_with_agent_add_to_cart_partial_success(self, client):
        with client.session_transaction() as sess:
            sess['state'] = {
                'pantry': {},
                'current_meal_plan': [],
                'current_shopping_list': [
                    {'name': 'apples', 'needed': 1},
                    {'name': 'unicorn', 'needed': 1}
                ],
                'user_preferences': {'zip_code': '12345'}
            }
        
        def mock_search(item_name, zip_code=None):
            if item_name == 'apples':
                return [{'productId': 'apple-123'}]
            return []
        
        with patch('app.search_kroger_products', side_effect=mock_search):
            with patch('app.add_items_to_kroger_cart', return_value=(True, 'Success')):
                response = client.post('/chat-with-agent', 
                                     json={'message': 'Add to cart'})
                
                assert response.status_code == 200
                data = response.get_json()
                assert 'I\'ve added 1 items' in data['message']
                assert 'couldn\'t find these items: unicorn' in data['message']

    def test_chat_with_agent_add_to_cart_api_failure(self, client):
        with client.session_transaction() as sess:
            sess['state'] = {
                'pantry': {},
                'current_meal_plan': [],
                'current_shopping_list': [{'name': 'apples', 'needed': 1}],
                'user_preferences': {'zip_code': '12345'}
            }
        
        with patch('app.search_kroger_products', return_value=[{'productId': 'apple-123'}]):
            with patch('app.add_items_to_kroger_cart', return_value=(False, 'API Error')):
                response = client.post('/chat-with-agent', 
                                     json={'message': 'Add to cart'})
                
                assert response.status_code == 200
                data = response.get_json()
                assert 'trouble adding items' in data['message']


if __name__ == '__main__':
    pytest.main([__file__])