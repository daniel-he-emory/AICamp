import pytest
import os
import tempfile
import json
from app import app, SessionState


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def sample_session_state():
    state = SessionState()
    state.pantry = {
        'tomatoes': 3,
        'onions': 2,
        'garlic': 5
    }
    state.user_preferences = {
        'zip_code': '12345'
    }
    state.current_meal_plan = [
        {
            'id': '52771',
            'name': 'Spicy Arrabiata Penne',
            'image': 'https://example.com/image.jpg',
            'ingredients': [
                {'name': 'penne pasta', 'measure': '1 pound'},
                {'name': 'tomatoes', 'measure': '1 can'},
                {'name': 'onions', 'measure': '1'},
                {'name': 'cheese', 'measure': '100g'}
            ]
        }
    ]
    state.current_shopping_list = [
        {'name': 'cheese', 'needed': 1},
        {'name': 'penne pasta', 'needed': 1}
    ]
    return state


@pytest.fixture
def mock_pantry_file(tmp_path):
    pantry_data = {
        'tomatoes': 3,
        'onions': 2,
        'garlic': 5
    }
    pantry_file = tmp_path / "pantry.json"
    pantry_file.write_text(json.dumps(pantry_data))
    return str(pantry_file)


@pytest.fixture
def sample_kroger_products():
    return [
        {
            'productId': 'kroger-123',
            'description': 'Organic Tomatoes',
            'brand': 'Simple Truth',
            'size': '1 lb'
        },
        {
            'productId': 'kroger-456',
            'description': 'Yellow Onions',
            'brand': 'Kroger',
            'size': '3 lb bag'
        }
    ]


@pytest.fixture
def sample_meal_db_response():
    return {
        'meals': [
            {
                'idMeal': '52771',
                'strMeal': 'Spicy Arrabiata Penne',
                'strMealThumb': 'https://www.themealdb.com/images/media/meals/ustsqw1468250014.jpg',
                'strIngredient1': 'penne rigate',
                'strIngredient2': 'olive oil',
                'strIngredient3': 'garlic',
                'strIngredient4': 'chopped tomatoes',
                'strIngredient5': 'red chile flakes',
                'strIngredient6': 'italian seasoning',
                'strIngredient7': 'basil',
                'strIngredient8': 'Parmigiano-Reggiano',
                'strIngredient9': '',
                'strIngredient10': '',
                'strMeasure1': '1 pound',
                'strMeasure2': '1/4 cup',
                'strMeasure3': '3 cloves',
                'strMeasure4': '1 tin',
                'strMeasure5': '1/2 teaspoon',
                'strMeasure6': '1/2 teaspoon',
                'strMeasure7': '6 leaves',
                'strMeasure8': 'spinkling',
                'strMeasure9': '',
                'strMeasure10': ''
            }
        ]
    }


@pytest.fixture
def sample_kroger_locations():
    return {
        'data': [
            {
                'locationId': 'store-123',
                'chain': 'KROGER',
                'name': 'Kroger #123',
                'address': {
                    'addressLine1': '123 Main St',
                    'city': 'Atlanta',
                    'state': 'GA',
                    'zipCode': '12345'
                }
            }
        ]
    }