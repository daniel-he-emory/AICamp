# GrocerGenie: AI Grocery Shopping Assistant

## API Credentials

### Kroger Access Token
```
eyJhbGciOiJSUzI1NiIsImprdSI6Imh0dHBzOi8vYXBpLmtyb2dlci5jb20vdjEvLndlbGwta25vd24vandrcy5qc29uIiwia2lkIjoiWjRGZDNtc2tJSDg4aXJ0N0xCNWM2Zz09IiwidHlwIjoiSldUIn0.eyJhdWQiOiJhaWNhbXAtYmJjNjc1ZDYiLCJleHAiOjE3NTExNTU0NDMsImlhdCI6MTc1MTE1MzYzOCwiaXNzIjoiYXBpLmtyb2dlci5jb20iLCJzdWIiOiI1MzgxZDNiMi1mM2JkLTU2NDYtYWI0Zi05YzZmNDUwNjg2NWQiLCJzY29wZSI6InByb2R1Y3QuY29tcGFjdCIsImF1dGhBdCI6MTc1MTE1MzY0Mzc2MzI3OTc0MCwiYXpwIjoiYWljYW1wLWJiYzY3NWQ2In0.aLG3GUODZEdqttlIEyKvtIurrfHuSUECjcSCKQO8JKVxT7REyBXhTm7RkQy6k0oDp5H1f20kXyRtHF1o5EJQ5412Zh0tkHCDvAOHr3X0oTnEfnbI2o1skfIYK4A5NAVPYmhTlzslhY7Ixsr7FFuEZW6P7yoovbuP8p4qfAq3eE4CCqjyc71XJnru6vOVPjEP6bG4tISOTQG6UkmcikdyD3n0nInM7Lz__MYr33_FtTtM2Eo6bJ9lEzoQArTsGANxnXjx2L7sM2pXpNDm0_hORktT1nL7En1W1JkOPEd2lColOmiO91L0dDv_H-NWURKNr7KFChIaiFnN2jyZwreu2A
```

## Project Requirements & Development Guide

### 1. Project Overview

**The Problem:** Meal planning is a recurring, time-consuming task involving recipe discovery, inventory checking, and shopping list creation, often leading to decision fatigue and food waste.

**Our Solution:** GrocerGenie is a smart shopping assistant that streamlines meal planning. It uses a conversational interface to understand user goals and current pantry inventory, intelligently plans meals, generates recipes, produces a precise shopping list of only the missing items, and uses an agentic tool to add those items to a real Kroger shopping cart.

### 2. Core Architecture: State Management

For the agent to have a coherent, multi-turn conversation, it must maintain a session state. This state will be a JSON object that keeps track of the conversation's context.

**session_state Object:**
- **pantry**: A JSON object representing the user's current pantry (e.g., {"onions": 2, "rice (bags)": 1}).
- **current_meal_plan**: A list of the recipes generated in the current request.
- **current_shopping_list**: The list of items needed for the current_meal_plan.
- **user_preferences**: Stores key user info like zip_code for locating a Kroger store.

### 3. Key Features & Development Plan

#### Feature 1: Conversational User Interaction & Intent Recognition

**Description:** The user interacts with GrocerGenie through a chat interface. The backend must determine the user's intent from their natural language messages.

**Development Steps:**
1. **Frontend:** A simple chat UI using HTML, CSS, and vanilla JavaScript.
2. **Backend (Flask):** A single `/chat-with-agent` endpoint that receives user messages.
3. **Intent Recognition (LLM Task):** Use an LLM call to classify the user's message into one of the following intents:
   - `update_pantry`
   - `check_pantry`
   - `request_meal_plan`
   - `add_to_cart`
   - `clarification` (for ambiguous inputs)
4. The backend triggers the appropriate feature logic based on the identified intent.

#### Feature 2: Conversational Pantry Management

**Description:** The agent dynamically populates and manages a pantry.json file through conversation.

**Development Steps:**
1. **Intent Check:** When the intent is `update_pantry`, process the user's message.
2. **Entity Extraction (LLM Task):** Send the user's message to an LLM with a prompt to extract food items, quantities, and the action (add, remove, or update).

   **User Message Example:** "I just bought two onions and a bag of rice, and I finished the milk."

   **Required LLM JSON Output:**
   ```json
   [
     {"item": "onion", "quantity": 2, "action": "add"},
     {"item": "rice", "quantity": 1, "action": "add"},
     {"item": "milk", "quantity": 0, "action": "remove"}
   ]
   ```
3. **Update pantry.json:** Parse the LLM's structured output. For "add", add or increment the item's quantity. For "remove", delete the item or set its quantity to 0.
4. **Confirmation:** Respond to the user with a confirmation message (e.g., "OK, I've added 2 onions and 1 bag of rice to your pantry and removed the milk.").

#### Feature 3: Recipe & Meal Plan Generation

**Description:** Fetches recipes from TheMealDB API based on a user's request.

**Development Steps:**
1. **Intent Check:** On `request_meal_plan`, extract key entities like cuisine type ("italian"), dietary restrictions, or number of meals.
2. **API Integration:** Make a GET request to TheMealDB API.
3. **Select & Parse:** Select the first 2-3 recipes from the API response and parse their data into a structured format (name, image, list of ingredients, and their measures). Store this in the `session_state.current_meal_plan`.

#### Feature 4: Ingredient Analysis & Shopping List Creation

**Description:** Compares the aggregated ingredients from the meal plan against the pantry.json to generate a shopping list of only what is missing.

**Development Steps:**
1. **Aggregate Ingredients:** Combine all ingredients from the `current_meal_plan`.
2. **Ingredient Normalization & Reconciliation (Critical Heuristic):** For each required ingredient, perform the following logic:
   - **a. Basic Match:** Check if a normalized version of the ingredient name exists in the pantry. (e.g., "Onions" → "onion").
   - **b. Synonym Match:** Check for common synonyms (e.g., "ground beef" vs. "beef mince").
   - **c. Quantity Check:** If a match is found, check if the quantity in the pantry is sufficient. This requires simple logic (e.g., if a recipe needs 1 onion and the pantry has 2, the need is met). For the MVP, do not attempt complex unit conversions. Assume a simple count is sufficient.
   - **d. Add to List:** If the item is not in the pantry or the quantity is insufficient, add it to the `current_shopping_list`.
3. **Return Response:** Present the meal plan and the final shopping list to the user in the chat interface.

#### Feature 5: UI Display of Results

**Description:** Dynamically render agent responses in the chat UI.

**Development Steps:**
1. **Structured Backend Responses:** The backend should send messages with a `type` field (e.g., `text`, `meal_plan`).
2. **Frontend Rendering Logic:** JavaScript will check the message type and render the appropriate HTML.
   - `text`: Simple paragraph.
   - `meal_plan`: A series of cards with recipe images, titles, and the final shopping list.

#### Feature 6: Agentic Shopping with Kroger API

**Description:** After a shopping list is approved by the user, the agent uses the Kroger API to add the items to the user's cart.

**Development Steps:**
1. **User Command:** Triggered by the `add_to_cart` intent (e.g., "Looks good, add them to my Kroger cart").
2. **Prerequisite Check:** If `user_preferences.zip_code` is not set, the agent must ask for it first. ("I need your zip code to find a nearby Kroger store. What is it?")
3. **Agentic Workflow (Decision Tree):** For each item in `session_state.current_shopping_list`:
   - **a. Search:** Use the `search_products` tool for the item.
   - **b. Handle No Results:** If the search returns zero items, inform the user: "I couldn't find [item name] at your Kroger. Would you like to skip it?"
   - **c. Handle Multiple Results:** If the search returns multiple items, apply a simple selection rule: select the first result (`productId` from the first item in the response). For this MVP, do not ask the user to choose.
   - **d. Collect IDs:** Add the selected `productId` to a temporary list.
4. **Bulk Add to Cart:** Once the loop is complete, call the `bulk_add_to_cart` tool with the collected list of product IDs.
5. **User Feedback:** Report the final status to the user in the chat (e.g., "I've added [X] items to your Kroger cart. I was unable to find [Y].").
