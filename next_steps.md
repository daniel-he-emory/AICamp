Detailed Roadmap for Next Iteration
Phase 1: LLM Integration (Critical Priority)
1.1 Replace Simple Intent Recognition with LLM
Current Issue: Using basic keyword matching instead of LLM-based intent recognition
Action Items:
Integrate an LLM service (OpenAI). Here is the Open AI API Key: __insert key___
Create prompt templates for intent classification
Update recognize_intent() function to use LLM
Add error handling for LLM API failures
Test Updates: Add tests for LLM integration and fallback behavior
1.2 Replace Simple Entity Extraction with LLM
Current Issue: Using basic string parsing instead of LLM-based entity extraction
Action Items:
Create structured prompts for extracting pantry items, quantities, and actions
Update extract_pantry_entities() to use LLM with JSON output
Handle complex natural language inputs (e.g., "I used up the last of the milk and bought 2 onions")
Test Updates: Add tests for complex entity extraction scenarios
Phase 2: Enhanced Ingredient Matching (High Priority)
2.1 Implement Ingredient Normalization
Current Issue: Basic string matching without synonyms or normalization
Action Items:
Create ingredient synonym mapping (e.g., "ground beef" = "beef mince")
Implement case-insensitive matching
Add unit normalization (e.g., "1 lb" = "16 oz")
Test Updates: Add tests for synonym matching and unit conversion
2.2 Improve Quantity Logic
Current Issue: Simple count-based comparison without unit conversion
Action Items:
Implement basic unit conversion (weight, volume, count)
Handle fractional quantities
Add tolerance for "close enough" matches
Test Updates: Add tests for unit conversion scenarios
Phase 3: Enhanced User Experience (Medium Priority)
3.1 Multi-turn Conversation Support
Current Issue: Limited context awareness across conversation turns
Action Items:
Enhance session state to track conversation history
Implement context-aware responses
Add conversation flow management
Test Updates: Add integration tests for multi-turn conversations
3.2 Better Error Handling and User Feedback
Current Issue: Generic error messages
Action Items:
Add specific error messages for different failure scenarios
Implement retry logic for API failures
Add user-friendly suggestions when items aren't found
Test Updates: Add tests for error scenarios and user feedback
Phase 4: Kroger Integration Improvements (Medium Priority)
4.1 Enhanced Product Selection
Current Issue: Always selects first product without user choice
Action Items:
Implement product ranking based on relevance
Add product details display (price, brand, size)
Consider user preferences for product selection
Test Updates: Add tests for product selection logic
4.2 Cart Management Features
Current Issue: Basic add-to-cart functionality
Action Items:
Add cart viewing capability
Implement item quantity management
Add cart clearing functionality
Test Updates: Add tests for cart management features
Phase 5: Data Persistence and Security (Low Priority)
5.1 Secure Session Management
Current Issue: Using Flask sessions which may not be production-ready
Action Items:
Implement proper session management with Redis or database
Add session expiration and cleanup
Implement secure user authentication
Test Updates: Add tests for session management and security
5.2 Data Validation and Sanitization
Current Issue: Limited input validation
Action Items:
Add comprehensive input validation
Implement data sanitization
Add rate limiting for API endpoints
Test Updates: Add tests for input validation and security
