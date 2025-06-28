/**
 * @jest-environment jsdom
 */

// Mock fetch globally
global.fetch = jest.fn();

// Set up DOM before loading script
document.body.innerHTML = `
  <div class="container">
    <div class="chat-container">
      <div id="chat-messages" class="chat-messages"></div>
      <div class="chat-input-container">
        <textarea id="chat-input" placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)" rows="1"></textarea>
        <button id="send-button">Send</button>
      </div>
    </div>
  </div>
`;

// Prevent the DOMContentLoaded event from firing automatically
const originalAddEventListener = document.addEventListener;
let domContentLoadedCallback;
document.addEventListener = jest.fn((event, callback) => {
  if (event === 'DOMContentLoaded') {
    domContentLoadedCallback = callback;
  } else {
    originalAddEventListener.call(document, event, callback);
  }
});

// Load the script and get the GrocerGenieChat class
const GrocerGenieChat = require('./script.js');

describe('GrocerGenieChat', () => {
  let grocerGenie;
  
  beforeEach(() => {
    // Reset DOM
    document.getElementById('chat-messages').innerHTML = '';
    document.getElementById('chat-input').value = '';
    document.getElementById('chat-input').style.height = '50px';
    document.getElementById('send-button').disabled = false;
    
    // Reset fetch mock
    fetch.mockClear();
    
    // Create new instance
    grocerGenie = new GrocerGenieChat();
  });
  
  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Constructor and Initialization', () => {
    test('should initialize chat elements correctly', () => {
      expect(grocerGenie.chatMessages).toBe(document.getElementById('chat-messages'));
      expect(grocerGenie.chatInput).toBe(document.getElementById('chat-input'));
      expect(grocerGenie.sendButton).toBe(document.getElementById('send-button'));
      expect(grocerGenie.chatContainer).toBe(document.querySelector('.chat-container'));
    });

    test('should set up event listeners', () => {
      const sendButton = document.getElementById('send-button');
      const chatInput = document.getElementById('chat-input');
      
      // Test click event listener exists
      expect(sendButton.onclick).toBeDefined();
      
      // Test enter key event listener
      const enterEvent = new KeyboardEvent('keypress', { key: 'Enter' });
      chatInput.dispatchEvent(enterEvent);
      // Should trigger sendMessage (we'll test this behavior in integration tests)
    });

    test('should scroll to bottom on initialization', async () => {
      const chatMessages = document.getElementById('chat-messages');
      
      // Mock requestAnimationFrame to execute immediately
      const originalRequestAnimationFrame = global.requestAnimationFrame;
      global.requestAnimationFrame = (callback) => {
        callback();
        return 1;
      };
      
      // Mock scrollHeight and scrollTop
      Object.defineProperty(chatMessages, 'scrollHeight', {
        value: 1000,
        configurable: true
      });
      Object.defineProperty(chatMessages, 'scrollTop', {
        value: 0,
        writable: true,
        configurable: true
      });
      
      // Create new instance to trigger initialization scroll
      new GrocerGenieChat();
      
      // Wait for next tick to ensure requestAnimationFrame has executed
      await new Promise(resolve => setTimeout(resolve, 0));
      
      expect(chatMessages.scrollTop).toBe(1000);
      
      // Restore original requestAnimationFrame
      global.requestAnimationFrame = originalRequestAnimationFrame;
    });
  });

  describe('Auto-resize Functionality', () => {
    test('should auto-resize textarea on input', () => {
      const chatInput = document.getElementById('chat-input');
      const originalHeight = chatInput.style.height;
      
      // Simulate typing a multi-line message
      chatInput.value = 'Line 1\nLine 2\nLine 3';
      chatInput.dispatchEvent(new Event('input'));
      
      // Height should have changed
      expect(chatInput.style.height).not.toBe(originalHeight);
    });

    test('should limit textarea height to maximum', () => {
      const chatInput = document.getElementById('chat-input');
      
      // Create a very long message that would exceed max height
      const longMessage = 'Line\n'.repeat(50);
      chatInput.value = longMessage;
      chatInput.dispatchEvent(new Event('input'));
      
      // Height should be limited to max-height (120px)
      const heightValue = parseInt(chatInput.style.height);
      expect(heightValue).toBeLessThanOrEqual(120);
    });

    test('should reset textarea height after sending message', async () => {
      const chatInput = document.getElementById('chat-input');
      
      // Set a custom height
      chatInput.style.height = '100px';
      chatInput.value = 'Test message';
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ type: 'text', message: 'Response' })
      });
      
      await grocerGenie.sendMessage();
      
      // Height should be reset to default
      expect(chatInput.style.height).toBe('50px');
    });
  });

  describe('Keyboard Handling', () => {
    test('should send message on Enter key press', () => {
      const chatInput = document.getElementById('chat-input');
      chatInput.value = 'Test message';
      
      // Mock sendMessage method
      grocerGenie.sendMessage = jest.fn();
      
      const enterEvent = new KeyboardEvent('keypress', { key: 'Enter' });
      chatInput.dispatchEvent(enterEvent);
      
      expect(grocerGenie.sendMessage).toHaveBeenCalled();
    });

    test('should not send message on Shift+Enter (should create new line)', () => {
      const chatInput = document.getElementById('chat-input');
      chatInput.value = 'Test message';
      
      // Mock sendMessage method
      grocerGenie.sendMessage = jest.fn();
      
      const shiftEnterEvent = new KeyboardEvent('keypress', { key: 'Enter', shiftKey: true });
      chatInput.dispatchEvent(shiftEnterEvent);
      
      expect(grocerGenie.sendMessage).not.toHaveBeenCalled();
    });

    test('should focus input after sending message', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ type: 'text', message: 'Response' })
      });
      
      const chatInput = document.getElementById('chat-input');
      chatInput.value = 'Test message';
      
      // Mock focus method
      chatInput.focus = jest.fn();
      
      await grocerGenie.sendMessage();
      
      expect(chatInput.focus).toHaveBeenCalled();
    });
  });

  describe('Message Management', () => {
    test('should add user message to chat', () => {
      const testMessage = 'Test user message';
      grocerGenie.addMessage(testMessage, 'user');
      
      const chatMessages = document.getElementById('chat-messages');
      const messageElements = chatMessages.querySelectorAll('.message');
      
      expect(messageElements.length).toBe(1);
      expect(messageElements[0]).toHaveClass('user-message');
      expect(messageElements[0].textContent).toContain(testMessage);
    });

    test('should add bot message to chat', () => {
      const testMessage = 'Test bot message';
      grocerGenie.addMessage(testMessage, 'bot');
      
      const chatMessages = document.getElementById('chat-messages');
      const messageElements = chatMessages.querySelectorAll('.message');
      
      expect(messageElements.length).toBe(1);
      expect(messageElements[0]).toHaveClass('bot-message');
      expect(messageElements[0].textContent).toContain(testMessage);
    });

    test('should handle DOM element as message content', () => {
      const testElement = document.createElement('div');
      testElement.textContent = 'Test element content';
      testElement.className = 'test-element';
      
      grocerGenie.addMessage(testElement, 'bot');
      
      const chatMessages = document.getElementById('chat-messages');
      const addedElement = chatMessages.querySelector('.test-element');
      
      expect(addedElement).not.toBeNull();
      expect(addedElement.textContent).toBe('Test element content');
    });

    test('should scroll to bottom after adding message', async () => {
      const chatMessages = document.getElementById('chat-messages');
      
      // Mock requestAnimationFrame to execute immediately
      const originalRequestAnimationFrame = global.requestAnimationFrame;
      global.requestAnimationFrame = (callback) => {
        callback();
        return 1;
      };
      
      // Mock scrollHeight and scrollTop
      Object.defineProperty(chatMessages, 'scrollHeight', {
        value: 1000,
        configurable: true
      });
      Object.defineProperty(chatMessages, 'scrollTop', {
        value: 0,
        writable: true,
        configurable: true
      });
      
      grocerGenie.addMessage('Test message', 'user');
      
      // Wait for next tick to ensure requestAnimationFrame has executed
      await new Promise(resolve => setTimeout(resolve, 0));
      
      expect(chatMessages.scrollTop).toBe(1000);
      
      // Restore original requestAnimationFrame
      global.requestAnimationFrame = originalRequestAnimationFrame;
    });
  });

  describe('Scrolling Behavior', () => {
    test('should use requestAnimationFrame for smooth scrolling', () => {
      const chatMessages = document.getElementById('chat-messages');
      
      // Mock requestAnimationFrame
      const mockRequestAnimationFrame = jest.fn();
      global.requestAnimationFrame = mockRequestAnimationFrame;
      
      // Mock scrollHeight and scrollTop
      Object.defineProperty(chatMessages, 'scrollHeight', {
        value: 1000,
        configurable: true
      });
      Object.defineProperty(chatMessages, 'scrollTop', {
        value: 0,
        writable: true,
        configurable: true
      });
      
      grocerGenie.scrollToBottom();
      
      expect(mockRequestAnimationFrame).toHaveBeenCalled();
    });

    test('should detect if scrolled to bottom', () => {
      const chatMessages = document.getElementById('chat-messages');
      
      // Mock properties for scrolled to bottom scenario
      Object.defineProperty(chatMessages, 'scrollTop', {
        value: 950,
        configurable: true
      });
      Object.defineProperty(chatMessages, 'clientHeight', {
        value: 100,
        configurable: true
      });
      Object.defineProperty(chatMessages, 'scrollHeight', {
        value: 1000,
        configurable: true
      });
      
      expect(grocerGenie.isScrolledToBottom()).toBe(true);
    });

    test('should detect if not scrolled to bottom', () => {
      const chatMessages = document.getElementById('chat-messages');
      
      // Mock properties for not scrolled to bottom scenario
      Object.defineProperty(chatMessages, 'scrollTop', {
        value: 0,
        configurable: true
      });
      Object.defineProperty(chatMessages, 'clientHeight', {
        value: 100,
        configurable: true
      });
      Object.defineProperty(chatMessages, 'scrollHeight', {
        value: 1000,
        configurable: true
      });
      
      expect(grocerGenie.isScrolledToBottom()).toBe(false);
    });
  });

  describe('Typing Indicator', () => {
    test('should show typing indicator', () => {
      grocerGenie.showTypingIndicator();
      
      const typingIndicator = document.getElementById('typing-indicator');
      expect(typingIndicator).not.toBeNull();
      expect(typingIndicator).toHaveClass('bot-message');
      
      const typingDots = typingIndicator.querySelector('.typing-dots');
      expect(typingDots).not.toBeNull();
      expect(typingDots.children.length).toBe(3);
    });

    test('should hide typing indicator', () => {
      grocerGenie.showTypingIndicator();
      expect(document.getElementById('typing-indicator')).not.toBeNull();
      
      grocerGenie.hideTypingIndicator();
      expect(document.getElementById('typing-indicator')).toBeNull();
    });

    test('should handle hiding non-existent typing indicator', () => {
      // Should not throw error
      expect(() => grocerGenie.hideTypingIndicator()).not.toThrow();
    });
  });

  describe('Meal Plan Rendering', () => {
    const sampleMealPlanData = {
      type: 'meal_plan',
      message: 'Here\'s your meal plan!',
      meal_plan: [
        {
          id: '1',
          name: 'Spaghetti Carbonara',
          image: 'https://example.com/carbonara.jpg',
          ingredients: [
            { name: 'pasta', measure: '400g' },
            { name: 'eggs', measure: '4' },
            { name: 'bacon', measure: '200g' }
          ]
        }
      ],
      shopping_list: [
        { name: 'eggs', needed: 2 },
        { name: 'bacon', needed: 1 }
      ]
    };

    test('should render meal plan correctly', () => {
      grocerGenie.renderMealPlan(sampleMealPlanData);
      
      const chatMessages = document.getElementById('chat-messages');
      const mealPlanCard = chatMessages.querySelector('.meal-plan-card');
      
      expect(mealPlanCard).not.toBeNull();
      expect(mealPlanCard.querySelector('h3').textContent).toBe('Spaghetti Carbonara');
      expect(mealPlanCard.querySelector('img').src).toBe('https://example.com/carbonara.jpg');
    });

    test('should render ingredients list in meal plan card', () => {
      grocerGenie.renderMealPlan(sampleMealPlanData);
      
      const chatMessages = document.getElementById('chat-messages');
      const ingredientsList = chatMessages.querySelector('.ingredients-list ul');
      
      expect(ingredientsList).not.toBeNull();
      expect(ingredientsList.children.length).toBe(3);
      expect(ingredientsList.children[0].textContent).toBe('400g pasta');
      expect(ingredientsList.children[1].textContent).toBe('4 eggs');
      expect(ingredientsList.children[2].textContent).toBe('200g bacon');
    });

    test('should render shopping list', () => {
      grocerGenie.renderMealPlan(sampleMealPlanData);
      
      const chatMessages = document.getElementById('chat-messages');
      const shoppingList = chatMessages.querySelector('.shopping-list');
      
      expect(shoppingList).not.toBeNull();
      expect(shoppingList.querySelector('h4').textContent).toBe('🛒 Shopping List');
      
      const shoppingItems = shoppingList.querySelectorAll('li');
      expect(shoppingItems.length).toBe(2);
      expect(shoppingItems[0].textContent).toBe('eggs (need 2)');
      expect(shoppingItems[1].textContent).toBe('bacon (need 1)');
    });

    test('should render call-to-action for shopping list', () => {
      grocerGenie.renderMealPlan(sampleMealPlanData);
      
      const chatMessages = document.getElementById('chat-messages');
      const ctaElement = chatMessages.querySelector('p strong');
      
      expect(ctaElement).not.toBeNull();
      expect(ctaElement.textContent).toContain('add to cart');
    });

    test('should handle meal plan without shopping list', () => {
      const dataWithoutShoppingList = {
        ...sampleMealPlanData,
        shopping_list: []
      };
      
      grocerGenie.renderMealPlan(dataWithoutShoppingList);
      
      const chatMessages = document.getElementById('chat-messages');
      const shoppingList = chatMessages.querySelector('.shopping-list');
      
      expect(shoppingList).toBeNull();
    });

    test('should handle meal plan card without image', () => {
      const dataWithoutImage = {
        ...sampleMealPlanData,
        meal_plan: [{
          id: '1',
          name: 'Simple Recipe',
          ingredients: [{ name: 'salt', measure: '1 tsp' }]
        }]
      };
      
      grocerGenie.renderMealPlan(dataWithoutImage);
      
      const chatMessages = document.getElementById('chat-messages');
      const mealPlanCard = chatMessages.querySelector('.meal-plan-card');
      const image = mealPlanCard.querySelector('img');
      
      expect(image).toBeNull();
    });

    test('should handle image loading error', () => {
      const dataWithInvalidImage = {
        ...sampleMealPlanData,
        meal_plan: [{
          id: '1',
          name: 'Recipe with Invalid Image',
          image: 'https://invalid-url.com/image.jpg',
          ingredients: []
        }]
      };
      
      grocerGenie.renderMealPlan(dataWithInvalidImage);
      
      const chatMessages = document.getElementById('chat-messages');
      const image = chatMessages.querySelector('img');
      
      expect(image).not.toBeNull();
      
      // Simulate image error
      image.dispatchEvent(new Event('error'));
      
      expect(image.style.display).toBe('none');
    });
  });

  describe('Bot Response Handling', () => {
    test('should handle text response', () => {
      const textResponse = {
        type: 'text',
        message: 'This is a text response'
      };
      
      grocerGenie.handleBotResponse(textResponse);
      
      const chatMessages = document.getElementById('chat-messages');
      const botMessage = chatMessages.querySelector('.bot-message');
      
      expect(botMessage).not.toBeNull();
      expect(botMessage.textContent).toContain('This is a text response');
    });

    test('should handle meal plan response', () => {
      const mealPlanResponse = {
        type: 'meal_plan',
        message: 'Here\'s your meal plan!',
        meal_plan: [
          {
            id: '1',
            name: 'Test Recipe',
            ingredients: []
          }
        ],
        shopping_list: []
      };
      
      grocerGenie.handleBotResponse(mealPlanResponse);
      
      const chatMessages = document.getElementById('chat-messages');
      const mealPlanCard = chatMessages.querySelector('.meal-plan-card');
      
      expect(mealPlanCard).not.toBeNull();
    });

    test('should handle response without type (default to text)', () => {
      const responseWithoutType = {
        message: 'Default text message'
      };
      
      grocerGenie.handleBotResponse(responseWithoutType);
      
      const chatMessages = document.getElementById('chat-messages');
      const botMessage = chatMessages.querySelector('.bot-message');
      
      expect(botMessage).not.toBeNull();
      expect(botMessage.textContent).toContain('Default text message');
    });
  });

  describe('Send Message Integration', () => {
    test('should not send empty message', async () => {
      document.getElementById('chat-input').value = '';
      
      await grocerGenie.sendMessage();
      
      expect(fetch).not.toHaveBeenCalled();
    });

    test('should not send whitespace-only message', async () => {
      document.getElementById('chat-input').value = '   ';
      
      await grocerGenie.sendMessage();
      
      expect(fetch).not.toHaveBeenCalled();
    });

    test('should send valid message and handle response', async () => {
      const mockResponse = {
        type: 'text',
        message: 'Bot response'
      };
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });
      
      document.getElementById('chat-input').value = 'Test message';
      
      await grocerGenie.sendMessage();
      
      expect(fetch).toHaveBeenCalledWith('http://localhost:5001/chat-with-agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: 'Test message' })
      });
      
      // Check that user message was added
      const chatMessages = document.getElementById('chat-messages');
      const userMessage = chatMessages.querySelector('.user-message');
      expect(userMessage.textContent).toContain('Test message');
      
      // Check that bot response was added
      const botMessage = chatMessages.querySelector('.bot-message');
      expect(botMessage.textContent).toContain('Bot response');
    });

    test('should handle fetch error gracefully', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));
      
      document.getElementById('chat-input').value = 'Test message';
      
      await grocerGenie.sendMessage();
      
      const chatMessages = document.getElementById('chat-messages');
      const errorMessage = chatMessages.querySelector('.bot-message');
      
      expect(errorMessage.textContent).toContain('encountered an error');
    });

    test('should disable send button during request', async () => {
      fetch.mockImplementationOnce(() => 
        new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: async () => ({ type: 'text', message: 'Response' })
        }), 100))
      );
      
      document.getElementById('chat-input').value = 'Test message';
      const sendButton = document.getElementById('send-button');
      
      const sendPromise = grocerGenie.sendMessage();
      
      // Button should be disabled during request
      expect(sendButton.disabled).toBe(true);
      
      await sendPromise;
      
      // Button should be re-enabled after request
      expect(sendButton.disabled).toBe(false);
    });

    test('should clear input after sending message', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ type: 'text', message: 'Response' })
      });
      
      const chatInput = document.getElementById('chat-input');
      chatInput.value = 'Test message';
      
      await grocerGenie.sendMessage();
      
      expect(chatInput.value).toBe('');
    });
  });

  describe('Event Listener Integration', () => {
    test('should send message on send button click', () => {
      const sendButton = document.getElementById('send-button');
      
      // Mock sendMessage method
      grocerGenie.sendMessage = jest.fn();
      
      sendButton.click();
      
      expect(grocerGenie.sendMessage).toHaveBeenCalled();
    });

    test('should not send message on other key press', () => {
      const chatInput = document.getElementById('chat-input');
      chatInput.value = 'Test message';
      
      // Mock sendMessage method
      grocerGenie.sendMessage = jest.fn();
      
      const spaceEvent = new KeyboardEvent('keypress', { key: ' ' });
      chatInput.dispatchEvent(spaceEvent);
      
      expect(grocerGenie.sendMessage).not.toHaveBeenCalled();
    });
  });

  describe('Edge Cases and Error Handling', () => {
    test('should handle malformed API response', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ /* missing required fields */ })
      });
      
      document.getElementById('chat-input').value = 'Test message';
      
      // Should not throw error
      await expect(grocerGenie.sendMessage()).resolves.not.toThrow();
    });

    test('should handle API response with null message', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ type: 'text', message: null })
      });
      
      document.getElementById('chat-input').value = 'Test message';
      
      await grocerGenie.sendMessage();
      
      // Should handle gracefully without crashing
      const chatMessages = document.getElementById('chat-messages');
      expect(chatMessages.children.length).toBeGreaterThan(0);
    });

    test('should handle very long messages', () => {
      const longMessage = 'A'.repeat(10000);
      
      grocerGenie.addMessage(longMessage, 'user');
      
      const chatMessages = document.getElementById('chat-messages');
      const messageElement = chatMessages.querySelector('.user-message');
      
      expect(messageElement.textContent).toContain(longMessage);
    });

    test('should handle special characters in messages', () => {
      const specialCharMessage = '<script>alert("xss")</script> & special chars: éñ中文';
      
      grocerGenie.addMessage(specialCharMessage, 'user');
      
      const chatMessages = document.getElementById('chat-messages');
      const messageElement = chatMessages.querySelector('.user-message');
      
      // Should escape HTML properly
      expect(messageElement.innerHTML).not.toContain('<script>');
      expect(messageElement.textContent).toContain('éñ中文');
    });
  });
});