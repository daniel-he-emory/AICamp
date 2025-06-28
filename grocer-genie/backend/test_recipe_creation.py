#!/usr/bin/env python3
"""
Test script for the new LLM recipe creation functionality
"""

from app import create_recipes_with_llm, normalize_ingredient_name, check_ingredient_availability

def test_recipe_creation():
    print("Testing LLM recipe creation...")
    
    # Test with various pantry combinations
    test_pantries = [
        {'eggs': 3, 'pasta': 1, 'olive oil': 1, 'garlic': 2},
        {'chicken': 1, 'rice': 1, 'onions': 2},
        {'beef': 1, 'tomatoes': 3, 'cheese': 1},
        {}  # Empty pantry
    ]
    
    for i, pantry in enumerate(test_pantries, 1):
        print(f"\n--- Test {i}: Pantry = {pantry} ---")
        recipes = create_recipes_with_llm(pantry)
        
        print(f"Created {len(recipes)} recipes:")
        for j, recipe in enumerate(recipes, 1):
            print(f"  {j}. {recipe['name']}")
            print(f"     Cooking time: {recipe['cooking_time']}")
            
            # Show ingredient availability
            available = [i['name'] for i in recipe['ingredients'] if i['has']]
            missing = [i['name'] for i in recipe['ingredients'] if not i['has']]
            print(f"     Available ingredients: {available}")
            print(f"     Missing ingredients: {missing}")
            
            # Show tips if available
            if 'tips' in recipe:
                print(f"     Tips: {recipe['tips']}")
            
            print()

def test_ingredient_matching():
    print("Testing ingredient matching...")
    
    pantry = {'eggs': 3, 'tomatoes': 2, 'olive oil': 1}
    
    # Test various ingredient names
    test_ingredients = ['eggs', 'tomatoes', 'milk', 'garlic', 'olive oil']
    
    for ingredient in test_ingredients:
        has_it, quantity = check_ingredient_availability(ingredient, pantry)
        status = f"✓ ({quantity})" if has_it else "✗"
        print(f"  {ingredient}: {status}")

if __name__ == '__main__':
    print("Testing new LLM recipe creation functionality...")
    print("=" * 60)
    
    test_ingredient_matching()
    test_recipe_creation()
    
    print("=" * 60)
    print("Recipe creation test completed!") 