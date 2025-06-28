# GrocerGenie: AI Grocery Shopping Assistant

### Project Requirements & Development Guide

### 1\. Project Overview

**The Problem:** Meal planning is a recurring, time-consuming, and often stressful task. It involves deciding what to eat, finding recipes, checking current inventory in the pantry and fridge, and compiling a precise shopping list. This process often leads to decision fatigue, forgotten ingredients, and food waste from over-purchasing.

**Our Solution:** GrocerGenie is a smart shopping assistant designed to eliminate the friction of weekly meal planning. By understanding a user's dietary goals and knowing the current state of their pantry, the agent intelligently plans meals for the week, generates recipes, produces an exact shopping list, and can even place the order for the user. This streamlines the entire process, saving users time, money, and mental energy.

**Hackathon Goal:** To build a functional Minimum Viable Product (MVP) that demonstrates the core logic: taking user input, referencing a simulated pantry, fetching recipes, generating a shopping list, and using an agentic tool to add those items to a real Kroger shopping cart.

### 2\. Key Features & Development Plan

This section breaks down each feature into its core function, step-by-step development instructions, and recommended tools for rapid prototyping.

#### Feature 1: User Preference & Dietary Input

* **Description:** The primary way the user interacts with GrocerGenie. The user will provide a simple text-based query describing the type of food they want to eat for the upcoming week.  
* **Development Steps:**  
  1. **Frontend:** Create a clean, simple UI with a prominent text input field and a "Generate Plan" button.  
  2. **Data Flow:** When the user clicks the button, the text from the input field is captured.  
  3. **API Call:** The frontend sends this text string to a backend API endpoint (e.g., /generate-meal-plan).  
* **Tools & Options:**  
  * **Frontend:** Use plain **HTML** for the structure (\<input type="text"\>, \<button\>). Use **vanilla JavaScript** to handle the button click event and make the fetch call to the backend.  
  * **Backend:** Define a route in **Flask** or a function in **Streamlit** that accepts a POST request with the user's query.

#### Feature 2: Simulated Pantry & Inventory Management

* **Description:** The "brain" of the assistant, representing the user's current food inventory. For the hackathon, this will be a static, pre-populated data store.  
* **Development Steps:**  
  1. **Create Data File:** In your project's root directory, create a file named pantry.json.  
  2. **Populate Data:** Structure the file as a simple JSON object. The keys are lowercase ingredient names, and the values represent their presence (a value of 1 is sufficient for the MVP).  
     {  
       "salt": 1,  
       "olive oil": 1,  
       "onion": 2,  
       "garlic": 5,  
       "canned tomatoes": 4,  
       "pasta": 2,  
       "rice": 1,  
       "chicken breast": 0,  
       "spinach": 0  
     }

  3. **Backend Logic:** Write a function in your Python backend that loads and parses this pantry.json file into a dictionary at the start of the request. This dictionary will be used for the ingredient comparison logic.  
* **Tools & Options:**  
  * **Storage:** A simple pantry.json file.  
  * **Backend:** Python's built-in json library (json.load()).

#### Feature 3: Recipe & Meal Plan Generation

* **Description:** Fetches recipes from an external source based on the user's query. The app will select a few recipes to constitute a simple "meal plan."  
* **Development Steps:**  
  1. **Receive Query:** The backend endpoint receives the user's query (e.g., "italian food").  
  2. **API Integration:** Make a GET request to a recipe API, using the query to search by cuisine, category, or ingredient.  
  3. **Select Recipes:** For simplicity, take the first 2-3 recipes from the API's response.  
  4. **Parse Data:** Extract the essential information for each recipe: its name, a direct image URL, and its list of ingredients and measurements. Store this in a structured format (like a list of dictionaries).  
* **Tools & Options:**  
  * **Recipe API:** **TheMealDB API** (www.themealdb.com/api.php) is perfect for a hackathon. It's free, requires no key for basic lookups, and allows searching by category (e.g., "Seafood", "Vegetarian") and area (e.g., "Italian", "Indian").  
  * **Backend:** Use the **requests library** in Python to make the HTTP calls to TheMealDB.

#### Feature 4: Ingredient Analysis & Shopping List Creation (Core Logic)

* **Description:** This is the central feature of the application. It compares the ingredients required for the meal plan against the user's pantry and determines exactly what is missing.  
* **Development Steps:**  
  1. **Aggregate Ingredients:** Combine the ingredient lists from all selected recipes into a single master list.  
  2. **Normalize Data:** Clean up the ingredient names from the recipe API. Convert them to lowercase and remove extra words to match the keys in your pentry.json file (e.g., "1 cup of Flour" becomes "flour"). This is a critical step.  
  3. **Compare & Contrast:** Iterate through the master ingredient list. For each item, check if its normalized name exists as a key in the pantry dictionary (and has a value \> 0).  
  4. **Build Shopping List:** If an ingredient is *not* found in the pantry, add it to a new list, which will become your final shopping list.  
  5. **Return Response:** Structure the final backend response as a JSON object containing both the meal plan (recipe names, images) and the generated shopping list.  
* **Tools & Options:**  
  * **Backend:** This logic can be implemented entirely in **pure Python** using dictionaries, lists, and loops. No special libraries are needed beyond the requests and json libraries already mentioned.

#### Feature 5: UI Display of Results

* **Description:** Presents the generated meal plan and shopping list to the user in a clear and organized way.  
* **Development Steps:**  
  1. **Frontend Sections:** Designate two areas in your HTML: one for the "Meal Plan" and one for the "Shopping List."  
  2. **Receive Data:** In your JavaScript fetch call, handle the .then() promise to receive the JSON response from the backend.  
  3. **Dynamic Rendering:**  
     * **Meal Plan:** Loop through the recipe data. For each recipe, dynamically create HTML elements (e.g., a \<div\> containing an \<img\> for the picture and an \<h3\> for the title) and append them to the "Meal Plan" section.  
     * **Shopping List:** Loop through the shopping list array. For each item, create an \<li\> element and append it to a \<ul\> in the "Shopping List" section.  
  4. **Clear Previous Results:** Ensure that each new search clears the previous results from the display.  
* **Tools & Options:**  
  * **Frontend:** **Vanilla JavaScript** using **DOM manipulation** (document.getElementById, document.createElement, element.innerHTML, element.appendChild).  
  * **Styling (Optional but Recommended):** Use a minimal CSS framework like **Pico.css** or **Water.css**. You just add one line to your HTML, and it provides beautiful, clean styling with no classes to write, which is perfect for a hackathon.

#### Feature 6: Agentic Shopping with Kroger API (NEW)

* **Description:** After the shopping list is generated, the user can command GrocerGenie to add the items to their Kroger shopping cart using the Kroger MCP Server.  
* **Development Steps:**  
  1. **Setup Kroger MCP Server:** The first priority is to get the Kroger MCP Server running. Follow the README.md instructions to register an application on the Kroger Developer Portal, get your credentials (CLIENT\_ID, CLIENT\_SECRET), and configure them in the server's environment.  
  2. **Extend UI:** Add a new button to the UI, "Add to Kroger Cart," which becomes active after a shopping list is generated.  
  3. **Agentic Workflow:** When the user clicks the new button, trigger the agentic shopping logic:  
     * **Find Products:** For each item in the generated shopping list, the agent must use the search\_products tool from the Kroger MCP to find the corresponding product at the user's preferred store. For the MVP, the agent can simply select the first result returned for each search term.  
     * **Collect Product IDs:** The agent will collect the productId for each item it finds.  
     * **Add to Cart:** Once all items have been searched, the agent will use the bulk\_add\_to\_cart tool, passing in the list of collected product IDs and their quantities.  
  4. **User Feedback:** The agent should report its progress back to the user, confirming which items were successfully found and added to the cart, and which (if any) could not be found.  
* **Tools & Options:**  
  * **Primary Tool:** The **Kroger MCP Server** as described in the provided README.md.  
  * **Backend:** The agent's core logic will orchestrate calls to the tools provided by the MCP server (search\_products, bulk\_add\_to\_cart).  
* **Key Considerations & Limitations:**  
  * **Authentication:** The agent must handle the initial user authentication flow required by the Kroger API. The MCP server documentation indicates this is handled via a browser prompt.  
  * **One-Way Cart:** As per the documentation, the Kroger Public API can **add** items to the cart but **cannot view or remove them**. The agent's dialogue with the user must make this clear. It should state, "I have added these items to your Kroger cart. To make changes or check out, please visit the Kroger app or website."  
  * **Store Location:** The agent should first ensure a preferred store location is set using the set\_preferred\_location tool, as product searches are location-specific.