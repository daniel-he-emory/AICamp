class GrocerGenieChat {
    constructor() {
        this.chatMessages = document.getElementById('chat-messages');
        this.chatInput = document.getElementById('chat-input');
        this.sendButton = document.getElementById('send-button');
        this.chatContainer = document.querySelector('.chat-container');
        
        this.initializeEventListeners();
        this.scrollToBottom();
    }
    
    initializeEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        this.chatInput.addEventListener('input', () => {
            this.autoResizeTextarea();
        });
        
        // Ensure chat input is visible when keyboard appears on mobile
        this.chatInput.addEventListener('focus', () => {
            setTimeout(() => this.scrollToBottom(), 100);
        });
    }
    
    autoResizeTextarea() {
        this.chatInput.style.height = 'auto';
        this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 120) + 'px';
    }
    
    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input and reset height
        this.chatInput.value = '';
        this.chatInput.style.height = '50px';
        
        // Disable send button
        this.sendButton.disabled = true;
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send message to backend
            const response = await fetch('http://localhost:5001/chat-with-agent', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            this.hideTypingIndicator();
            
            // Handle different response types
            this.handleBotResponse(data);
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        } finally {
            this.sendButton.disabled = false;
            this.chatInput.focus();
        }
    }
    
    addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        if (typeof content === 'string') {
            const p = document.createElement('p');
            p.textContent = content;
            messageContent.appendChild(p);
        } else {
            messageContent.appendChild(content);
        }
        
        messageDiv.appendChild(messageContent);
        this.chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom with smooth animation
        this.scrollToBottom();
    }
    
    scrollToBottom() {
        // Use requestAnimationFrame for smooth scrolling
        requestAnimationFrame(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        });
    }
    
    isScrolledToBottom() {
        const threshold = 50; // pixels from bottom
        return this.chatMessages.scrollTop + this.chatMessages.clientHeight >= 
               this.chatMessages.scrollHeight - threshold;
    }
    
    handleBotResponse(data) {
        if (data.type === 'meal_plan') {
            this.renderMealPlan(data);
        } else {
            this.addMessage(data.message, 'bot');
        }
    }
    
    renderMealPlan(data) {
        const container = document.createElement('div');
        
        // Add intro message
        const intro = document.createElement('p');
        intro.textContent = data.message;
        container.appendChild(intro);
        
        // Render meal plan cards
        data.meal_plan.forEach(recipe => {
            const card = this.createMealPlanCard(recipe);
            container.appendChild(card);
        });
        
        // Render shopping list
        if (data.shopping_list && data.shopping_list.length > 0) {
            const shoppingListDiv = this.createShoppingList(data.shopping_list);
            container.appendChild(shoppingListDiv);
            
            // Add call-to-action
            const cta = document.createElement('p');
            cta.innerHTML = '<strong>Say "add to cart" to add these items to your Kroger cart!</strong>';
            cta.style.marginTop = '15px';
            cta.style.color = '#4CAF50';
            container.appendChild(cta);
        }
        
        this.addMessage(container, 'bot');
    }
    
    createMealPlanCard(recipe) {
        const card = document.createElement('div');
        card.className = 'meal-plan-card';
        
        const title = document.createElement('h3');
        title.textContent = recipe.name;
        card.appendChild(title);
        
        if (recipe.image) {
            const img = document.createElement('img');
            img.src = recipe.image;
            img.alt = recipe.name;
            img.onerror = () => {
                img.style.display = 'none';
            };
            card.appendChild(img);
        }
        
        if (recipe.ingredients && recipe.ingredients.length > 0) {
            const ingredientsTitle = document.createElement('h4');
            ingredientsTitle.textContent = 'Ingredients:';
            ingredientsTitle.style.marginTop = '10px';
            card.appendChild(ingredientsTitle);
            
            const ingredientsList = document.createElement('div');
            ingredientsList.className = 'ingredients-list';
            
            const ul = document.createElement('ul');
            recipe.ingredients.forEach(ingredient => {
                const li = document.createElement('li');
                li.textContent = `${ingredient.measure} ${ingredient.name}`.trim();
                ul.appendChild(li);
            });
            
            ingredientsList.appendChild(ul);
            card.appendChild(ingredientsList);
        }
        
        return card;
    }
    
    createShoppingList(shoppingList) {
        const container = document.createElement('div');
        container.className = 'shopping-list';
        
        const title = document.createElement('h4');
        title.textContent = '🛒 Shopping List';
        container.appendChild(title);
        
        const ul = document.createElement('ul');
        shoppingList.forEach(item => {
            const li = document.createElement('li');
            li.textContent = `${item.name} (need ${item.needed})`;
            ul.appendChild(li);
        });
        
        container.appendChild(ul);
        return container;
    }
    
    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message';
        typingDiv.id = 'typing-indicator';
        
        const typingContent = document.createElement('div');
        typingContent.className = 'typing-indicator';
        
        const typingDots = document.createElement('div');
        typingDots.className = 'typing-dots';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            typingDots.appendChild(dot);
        }
        
        typingContent.appendChild(typingDots);
        typingDiv.appendChild(typingContent);
        this.chatMessages.appendChild(typingDiv);
        
        // Scroll to bottom
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
}

// Initialize the chat when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new GrocerGenieChat();
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GrocerGenieChat;
}