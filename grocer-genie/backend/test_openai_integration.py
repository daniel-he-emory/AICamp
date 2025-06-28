import pytest
import json
from unittest.mock import patch, MagicMock
from app import (
    call_openai_with_fallback, get_intent_classification_prompt, 
    get_entity_extraction_prompt, recognize_intent, extract_pantry_entities
)


class TestOpenAIIntegration:
    """Test LLM integration and fallback behavior"""
    
    def test_call_openai_with_fallback_success(self):
        """Test successful OpenAI API call"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "update_pantry"
        
        with patch('openai.ChatCompletion.create', return_value=mock_response):
            result, error = call_openai_with_fallback([{"role": "user", "content": "test"}])
            
            assert result == "update_pantry"
            assert error is None
    
    def test_call_openai_with_fallback_api_error(self):
        """Test OpenAI API failure and error handling"""
        with patch('openai.ChatCompletion.create', side_effect=Exception("API Error")):
            result, error = call_openai_with_fallback([{"role": "user", "content": "test"}])
            
            assert result is None
            assert "API Error" in error
    
    def test_intent_classification_prompt_format(self):
        """Test intent classification prompt is properly formatted"""
        prompt = get_intent_classification_prompt()
        formatted = prompt.format(message="I bought apples")
        
        assert "I bought apples" in formatted
        assert "update_pantry" in formatted
        assert "check_pantry" in formatted
        assert "request_meal_plan" in formatted
        assert "add_to_cart" in formatted
        assert "clarification" in formatted
    
    def test_entity_extraction_prompt_format(self):
        """Test entity extraction prompt is properly formatted"""
        prompt = get_entity_extraction_prompt()
        formatted = prompt.format(message="I bought 2 onions")
        
        assert "I bought 2 onions" in formatted
        assert "JSON" in formatted
        assert "item" in formatted
        assert "quantity" in formatted
        assert "action" in formatted


class TestLLMIntentRecognition:
    """Test LLM-powered intent recognition with fallbacks"""
    
    @patch('app.call_openai_with_fallback')
    def test_recognize_intent_llm_success(self, mock_llm):
        """Test successful LLM intent recognition"""
        mock_llm.return_value = ("update_pantry", None)
        
        result = recognize_intent("I bought 3 apples and finished the milk")
        
        assert result == "update_pantry"
        mock_llm.assert_called_once()
    
    @patch('app.call_openai_with_fallback')
    def test_recognize_intent_llm_invalid_response(self, mock_llm):
        """Test LLM returns invalid intent, falls back to keyword matching"""
        mock_llm.return_value = ("invalid_intent", None)
        
        result = recognize_intent("I bought 3 apples")
        
        # Should fall back to keyword matching
        assert result == "update_pantry"
    
    @patch('app.call_openai_with_fallback')
    def test_recognize_intent_llm_failure(self, mock_llm):
        """Test LLM failure, falls back to keyword matching"""
        mock_llm.return_value = (None, "API Error")
        
        result = recognize_intent("What's in my pantry?")
        
        # Should fall back to keyword matching
        assert result == "check_pantry"
    
    @patch('app.call_openai_with_fallback')
    def test_recognize_intent_complex_messages(self, mock_llm):
        """Test complex natural language messages"""
        test_cases = [
            ("I just went shopping and got some chicken breast, 2 pounds of ground beef, and a bag of rice", "update_pantry"),
            ("Can you show me what ingredients I currently have available in my kitchen?", "check_pantry"),
            ("I'm in the mood for some Italian cuisine tonight, maybe pasta or risotto", "request_meal_plan"),
            ("Please add all the items from my shopping list to my Kroger cart", "add_to_cart")
        ]
        
        for message, expected_intent in test_cases:
            mock_llm.return_value = (expected_intent, None)
            result = recognize_intent(message)
            assert result == expected_intent


class TestLLMEntityExtraction:
    """Test LLM-powered entity extraction with fallbacks"""
    
    @patch('app.call_openai_with_fallback')
    def test_extract_pantry_entities_llm_success(self, mock_llm):
        """Test successful LLM entity extraction"""
        mock_response = '[{"item": "onion", "quantity": 2, "action": "add"}, {"item": "milk", "quantity": 0, "action": "remove"}]'
        mock_llm.return_value = (mock_response, None)
        
        result = extract_pantry_entities("I bought 2 onions and finished the milk")
        
        assert len(result) == 2
        assert result[0]["item"] == "onion"
        assert result[0]["quantity"] == 2
        assert result[0]["action"] == "add"
        assert result[1]["item"] == "milk"
        assert result[1]["action"] == "remove"
    
    @patch('app.call_openai_with_fallback')
    def test_extract_pantry_entities_invalid_json(self, mock_llm):
        """Test LLM returns invalid JSON, falls back to simple parsing"""
        mock_llm.return_value = ("invalid json", None)
        
        result = extract_pantry_entities("I bought 3 apples")
        
        # Should fall back to simple parsing
        assert len(result) == 1
        assert result[0]["item"] == "apples"
        assert result[0]["quantity"] == 3
        assert result[0]["action"] == "add"
    
    @patch('app.call_openai_with_fallback')
    def test_extract_pantry_entities_invalid_structure(self, mock_llm):
        """Test LLM returns valid JSON but invalid structure"""
        mock_response = '[{"wrong": "structure"}]'
        mock_llm.return_value = (mock_response, None)
        
        result = extract_pantry_entities("I finished milk")
        
        # Should fall back to simple parsing
        assert len(result) == 1
        assert result[0]["item"] == "milk"
        assert result[0]["action"] == "remove"
    
    @patch('app.call_openai_with_fallback')
    def test_extract_pantry_entities_llm_failure(self, mock_llm):
        """Test LLM failure, falls back to simple parsing"""
        mock_llm.return_value = (None, "API Error")
        
        result = extract_pantry_entities("I added 5 oranges")
        
        # Should fall back to simple parsing
        assert len(result) == 1
        assert result[0]["item"] == "oranges"
        assert result[0]["quantity"] == 5
        assert result[0]["action"] == "add"


class TestComplexEntityExtractionScenarios:
    """Test complex natural language entity extraction scenarios"""
    
    @patch('app.call_openai_with_fallback')
    def test_complex_shopping_message(self, mock_llm):
        """Test complex shopping scenario"""
        mock_response = '''[
            {"item": "chicken breast", "quantity": 2, "action": "add"},
            {"item": "ground beef", "quantity": 1, "action": "add"},
            {"item": "rice", "quantity": 1, "action": "add"},
            {"item": "milk", "quantity": 0, "action": "remove"},
            {"item": "egg", "quantity": 3, "action": "remove"}
        ]'''
        mock_llm.return_value = (mock_response, None)
        
        message = "I just went shopping and bought 2 pounds of chicken breast, 1 pound of ground beef, and a bag of rice. I also used up the last of the milk and 3 eggs for breakfast."
        result = extract_pantry_entities(message)
        
        assert len(result) == 5
        
        # Check add actions
        chicken = next(item for item in result if item["item"] == "chicken breast")
        assert chicken["quantity"] == 2
        assert chicken["action"] == "add"
        
        # Check remove actions
        milk = next(item for item in result if item["item"] == "milk")
        assert milk["quantity"] == 0
        assert milk["action"] == "remove"
        
        eggs = next(item for item in result if item["item"] == "egg")
        assert eggs["quantity"] == 3
        assert eggs["action"] == "remove"
    
    @patch('app.call_openai_with_fallback')
    def test_mixed_units_and_quantities(self, mock_llm):
        """Test extraction with mixed units and quantities"""
        mock_response = '''[
            {"item": "apple", "quantity": 6, "action": "add"},
            {"item": "bread", "quantity": 2, "action": "add"},
            {"item": "cheese", "quantity": 1, "action": "add"},
            {"item": "pasta", "quantity": 1, "action": "remove"}
        ]'''
        mock_llm.return_value = (mock_response, None)
        
        message = "I picked up half a dozen apples, 2 loaves of bread, and some cheese. I used up the last box of pasta."
        result = extract_pantry_entities(message)
        
        assert len(result) == 4
        
        apples = next(item for item in result if item["item"] == "apple")
        assert apples["quantity"] == 6  # LLM should convert "half a dozen" to 6
        
        bread = next(item for item in result if item["item"] == "bread")
        assert bread["quantity"] == 2
    
    @patch('app.call_openai_with_fallback')
    def test_implicit_quantities(self, mock_llm):
        """Test extraction when quantities are implicit"""
        mock_response = '''[
            {"item": "tomato", "quantity": 1, "action": "add"},
            {"item": "onion", "quantity": 1, "action": "add"},
            {"item": "garlic", "quantity": 1, "action": "add"}
        ]'''
        mock_llm.return_value = (mock_response, None)
        
        message = "I got some tomatoes, an onion, and garlic from the store"
        result = extract_pantry_entities(message)
        
        assert len(result) == 3
        for item in result:
            assert item["quantity"] == 1  # Should default to 1 when not specified
            assert item["action"] == "add"
    
    @patch('app.call_openai_with_fallback')
    def test_synonyms_and_variations(self, mock_llm):
        """Test extraction with food name variations and synonyms"""
        mock_response = '''[
            {"item": "ground beef", "quantity": 1, "action": "add"},
            {"item": "bell pepper", "quantity": 3, "action": "add"},
            {"item": "soda", "quantity": 6, "action": "add"}
        ]'''
        mock_llm.return_value = (mock_response, None)
        
        message = "I bought some beef mince, 3 bell peppers, and a six-pack of soda"
        result = extract_pantry_entities(message)
        
        assert len(result) == 3
        
        beef = next(item for item in result if "beef" in item["item"])
        assert beef["action"] == "add"
        
        peppers = next(item for item in result if "pepper" in item["item"])
        assert peppers["quantity"] == 3


class TestFallbackBehavior:
    """Test fallback behavior when LLM fails"""
    
    @patch('app.call_openai_with_fallback')
    def test_intent_fallback_maintains_functionality(self, mock_llm):
        """Test that intent recognition still works when LLM fails"""
        mock_llm.return_value = (None, "API Error")
        
        # Test all intent types still work with keyword matching
        test_cases = [
            ("What's in my pantry?", "check_pantry"),
            ("I bought apples", "update_pantry"),
            ("Show me recipes", "request_meal_plan"),
            ("Add to cart", "add_to_cart"),
            ("Hello", "clarification")
        ]
        
        for message, expected_intent in test_cases:
            result = recognize_intent(message)
            assert result == expected_intent
    
    @patch('app.call_openai_with_fallback')
    def test_entity_extraction_fallback_maintains_functionality(self, mock_llm):
        """Test that entity extraction still works when LLM fails"""
        mock_llm.return_value = (None, "API Error")
        
        # Test basic patterns still work
        result = extract_pantry_entities("I bought 3 apples")
        assert len(result) == 1
        assert result[0]["item"] == "apples"
        assert result[0]["quantity"] == 3
        assert result[0]["action"] == "add"
        
        result = extract_pantry_entities("I finished milk")
        assert len(result) == 1
        assert result[0]["item"] == "milk"
        assert result[0]["action"] == "remove"


if __name__ == '__main__':
    pytest.main([__file__])