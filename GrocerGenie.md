# GrocerGenie: AI Grocery Shopping Assistant

## API Credentials

### Kroger Access Token
```
eyJhbGciOiJSUzI1NiIsImprdSI6Imh0dHBzOi8vYXBpLmtyb2dlci5jb20vdjEvLndlbGwta25vd24vandrcy5qc29uIiwia2lkIjoiWjRGZDNtc2tJSDg4aXJ0N0xCNWM2Zz09IiwidHlwIjoiSldUIn0.eyJhdWQiOiJhaWNhbXAtYmJjNjc1ZDYiLCJleHAiOjE3NTExNDIyOTUsImlhdCI6MTc1MTE0MDQ5MCwiaXNzIjoiYXBpLmtyb2dlci5jb20iLCJzdWIiOiI1MzgxZDNiMi1mM2JkLTU2NDYtYWI0Zi05YzZmNDUwNjg2NWQiLCJzY29wZSI6InByb2R1Y3QuY29tcGFjdCIsImF1dGhBdCI6MTc1MTE0MDQ5NTQ0MDgyMzk2NCwiYXpwIjoiYWljYW1wLWJiYzY3NWQ2In0.FPrEA7NBTTy_jgLK0xrB-la4hoBUHDO7cmaApJUmtyNSTw1EyiN9T9P8HOFHIE8pqTwTBIKczP4gbnirPe7LcB689CGO68I8TXUP0QTxFQGZNDnAcrUiQKPySo1484OXZO34OtiRN9KXrNfVXUdVQ5-8bxeYmFAZyOMZMrjJ_tCA8lIqUX_3a0DK29Lir2VCROvHqs1KFczq460oQILUtII4XDCSalGpYLY2EU2nNwNzJIV4yr8EjDIlH9gZoPkE4OoQQPNMCWHdNYwWetZ87IFcST7YEOpSu6bZtSMW8I6RSLcWDiegW22RfpcRJzqZ_cSLS2ybZad1iC04Ricm4Q
```

### Project Requirements & Development Guide

### 1\. Project Overview

**The Problem:** Meal planning is a recurring, time-consuming, and often stressful task. It involves deciding what to eat, finding recipes, checking current inventory in the pantry and fridge, and compiling a precise shopping list. This process often leads to decision fatigue, forgotten ingredients, and food waste from over-purchasing.

**Our Solution:** GrocerGenie is a smart shopping assistant designed to eliminate the friction of weekly meal planning. By **chatting with the user** to understand their dietary goals and the current state of their pantry, the agent intelligently plans meals for the week, generates recipes, produces an exact shopping list, and can even place the order for the user. This streamlines the entire process, saving users time, money, and mental energy.

**Hackathon Goal:** To build a functional Minimum Viable Product (MVP) that demonstrates the core logic: **conversationally populating a pantry**, taking user meal preferences, fetching recipes, generating a shopping list, and using an agentic tool to add those items to a real Kroger shopping cart.

### 2\. Key Features & Development Plan

This section breaks down each feature into its core function, step-by-step development instructions, and recommended tools for rapid prototyping.

#### Feature 1: Conversational User Interaction

* **Description:** The primary way the user interacts with GrocerGenie is through a chat interface. The user will provide natural language commands to manage their pantry and request meal plans.  
* **Development Steps:**  
  1. **Frontend:** Create a chat-style UI. This will include a message history display area and a text input field for the user to type their messages.  
  2. **Data Flow:** When the user sends a message, the text is sent to a central backend endpoint (e.g., /chat-with-agent).  
  3. **Backend Logic:** The backend will receive the text and use an LLM to determine the user's *intent* (e.g., "update pantry," "request meal plan"). Based on the intent, it will trigger the appropriate feature logic.  
* **Tools & Options:**  
  * **Frontend:** A simple chat UI built with **HTML, CSS, and vanilla JavaScript**.  
  * **Backend:** A single, robust route in **Flask**.  
  * **Intent Recognition:** An **LLM call** (e.g., to a model like Claude or a local model) to classify the user's intent from their message text.

#### Feature 2: Conversational Pantry Management (Revised)

* **Description:** The agent populates and manages the user's pantry inventory through natural language conversation. The pantry.json file is no longer static but a dynamic database updated by the agent.  
* **Development Steps:**  
  1. **Initialize Pantry:** The pantry.json file can start as an empty JSON object {}.  
  2. **Intent Check:** When the backend agent determines the user's intent is to "update pantry," it processes the message text.  
  3. **Entity Extraction (LLM Task):** The agent sends the user's message (e.g., "I have two onions and a bag of rice") to an LLM with a specific prompt to extract the food items and their quantities. The prompt should ask for a structured output, like JSON.  
     * *Example LLM Output:* \[{"item": "onion", "quantity": 2}, {"item": "rice", "quantity": 1}\]  
  4. **Update Pantry File:** The backend logic parses the structured output from the LLM and updates the pantry.json file on the server.  
  5. **Confirmation:** The agent sends a confirmation message back to the user (e.g., "OK, I've updated your pantry.").  
* **Tools & Options:**  
  * **Core Tool:** An **LLM API** is essential for this feature to perform the entity extraction.  
  * **Storage:** A dynamic pantry.json file that the server can read from and write to.  
  * **Backend:** Python's built-in json library to handle reading and writing to the pantry file.

#### Feature 3: Recipe & Meal Plan Generation

* **Description:** Fetches recipes from an external source based on the user's conversational request.  
* **Development Steps:**  
  1. **Receive Query:** The agent identifies the intent "request meal plan" and extracts the cuisine type (e.g., "italian food") from the user's message.  
  2. **API Integration:** Make a GET request to a recipe API.  
  3. **Select & Parse:** Select the first 2-3 recipes and parse their data (name, image, ingredients).  
* **Tools & Options:**  
  * **Recipe API:** **TheMealDB API** (www.themealdb.com/api.php).  
  * **Backend:** **requests library** in Python.

#### Feature 4: Ingredient Analysis & Shopping List Creation

* **Description:** Compares the ingredients for the meal plan against the now-dynamic pantry and determines what's missing.  
* **Development Steps:**  
  1. **Read Current Pantry:** Load the latest state of the pantry.json file.  
  2. **Aggregate & Normalize:** Combine ingredients from the recipes and normalize their names.  
  3. **Compare & Build List:** Iterate through the required ingredients, check against the pantry, and build the shopping list of missing items.  
  4. **Return Response:** The agent presents the meal plan and shopping list back to the user in the chat interface.  
* **Tools & Options:**  
  * **Backend:** Pure Python logic.

#### Feature 5: UI Display of Results

* **Description:** Presents all results (confirmations, meal plans, shopping lists) within the chat interface.  
* **Development Steps:**  
  1. **Frontend Logic:** The JavaScript controlling the chat UI must be able to render different types of messages from the agent.  
  2. **Structured Messages:** The backend should send structured responses. For a meal plan, it might send a message with a type: "meal\_plan" and a data payload containing the recipes and list.  
  3. **Dynamic Rendering:** The frontend JavaScript will check the message type and render the appropriate HTML. Simple text for confirmations, and more complex card-based layouts for recipes and lists, all appended to the chat history.  
* **Tools & Options:**  
  * **Frontend:** **Vanilla JavaScript** DOM manipulation.

#### Feature 6: Agentic Shopping with Kroger API

* **Description:** After the shopping list is generated and displayed in the chat, the user can command GrocerGenie to add the items to their Kroger cart.  
* **Development Steps:**  
  1. **Setup Kroger MCP Server:** This remains the first priority. You can find the documentation for the Kroger MCP Server under external_tools_docs/ in this repo. Use it to make sure your calls to the server are correct.  
  2. **User Command:** The user gives a command like, "Okay, add those to my Kroger cart."  
  3. **Agentic Workflow:** The agent identifies the "add to cart" intent and executes the workflow:  
     * Use the search\_products tool for each item on the list.  
     * Collect the productId for each item.  
     * Use the bulk\_add\_to\_cart tool.  
  4. **User Feedback:** The agent reports its progress and success/failure back to the user in the chat interface.  
* **Tools & Options:**  
  * **Primary Tool:** The **Kroger MCP Server**.  
* **Key Considerations & Limitations:**  
  * **Authentication & One-Way Cart:** These remain the same. The agent must handle the auth flow and clearly communicate the limitations of the Kroger API to the user via chat.  
  * **Store Location:** The agent should initiate a conversation to set the user's preferred store if it isn't already set. ("I see you want to shop at Kroger. What is your zip code so I can find the nearest stores?")
