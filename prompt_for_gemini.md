GrocerGenie: 5-Hour AI MCP Hackathon Plan
The goal is to build a functional Minimum Viable Product (MVP) that demonstrates the core agentic loop: taking a user's meal preference, checking a simulated pantry, generating a shopping list, and using the Kroger MCP Server to add those items to a real shopping cart.

1. The Core Concept (Hackathon MVP)
A user specifies a meal they want to cook. The app checks a hardcoded list of ingredients for that meal against a hardcoded pantry list. It generates a shopping list of what's missing and then uses the Kroger MCP agent to find those items and add them to the user's cart.

Key to Winning: Don't try to build the full "learning" agent. Focus entirely on a single, successful end-to-end demonstration. The "wow" factor comes from seeing a meal plan turn into a populated Kroger cart automatically.

2. Recommended Tech Stack (Speed is Everything)
Primary Tool: Kroger MCP Server. This is the star of the show. Your project's success is directly tied to using its tools. The GitHub repository CupOfOwls/kroger-mcp is your primary resource.

Agent Logic / Backend: Python. It's the lingua franca of AI and what you'll use to script the interactions with the MCP server.

User Interface (UI): Streamlit. Do not attempt to build a traditional web frontend with HTML/JS/Flask. Streamlit allows you to create a simple, effective UI with just a few lines of Python. It's the fastest way to build a demoable interface for a data-driven script.

Data Storage (Pantry & Recipes): Hardcoded Python Dictionaries. Do not use .json files or a database. For a 5-hour hackathon, defining your data directly in your Python script (pantry = {...}, recipes = {...}) is the fastest and most reliable method.

3. The 5-Hour Development Roadmap
This aggressive schedule prioritizes the biggest risks first.

Hour 1: Setup & Authentication (The Foundation)
Goal: Get the Kroger MCP Server running locally and successfully authenticate. This is the most critical and potentially time-consuming step.

Tasks:

Register on Kroger Developer Portal: Immediately create an account and register an application. You need your CLIENT_ID and CLIENT_SECRET.

Clone & Configure: Clone the CupOfOwls/kroger-mcp repository. Create a .env file and populate it with your Kroger API credentials.

Run the Server: Follow the README instructions to install dependencies (uv is recommended) and launch the server.

Authenticate: The first time you try to use a tool that requires user data (like finding stores), the server will prompt you to authenticate via a web browser. Complete this flow. You cannot proceed without this.

Test a Tool: Use a simple command-line tool like curl or a simple Python script to call a basic tool from your running MCP server, like search_locations. If you get a valid response, you are ready for the next step.

Hour 2: The Core Logic (Pantry & Planner)
Goal: Write the "brain" of your app in a single Python script. This part does not involve the MCP server yet.

Tasks (main.py):

Hardcode the Pantry: At the top of your script, define your simulated pantry.

Python

pantry = {
    "salt": 1, "pepper": 1, "olive oil": 1,
    "onion": 0, "garlic": 0, "chicken breast": 0
}
Hardcode Recipes: Define a few simple recipes. The ingredients should be simple, lowercase strings.

Python

recipes = {
    "lemon chicken": {
        "name": "Lemon Herb Chicken",
        "ingredients": ["chicken breast", "olive oil", "garlic", "lemon"]
    },
    "simple pasta": {
        "name": "Garlic Tomato Pasta",
        "ingredients": ["pasta", "canned tomatoes", "garlic", "onion"]
    }
}
Write the Comparison Logic: Create a Python function generate_shopping_list(meal_choice) that takes a key (e.g., "lemon chicken"), finds the recipe, and compares its ingredients to the pantry. It should return a list of missing items.

Example: generate_shopping_list("lemon chicken") should return ['chicken breast', 'garlic', 'lemon'].

Hour 3: The Agentic Workflow (Connecting to Kroger)
Goal: Connect your core logic to the Kroger MCP server to find products.

Tasks (Continue in main.py):

Integrate requests: Use Python's requests library to make calls to your locally running MCP server (e.g., http://127.0.0.1:8000/tools/search_products).

Set Preferred Location: Your first agentic action must be to set a store. Hardcode a zip code and call the set_preferred_location tool.

Build the find_products function: Create a function that takes your generated shopping list. For each item in the list:

It should call the search_products tool via an HTTP request.

It should parse the JSON response and grab the productId and name of the first result for simplicity.

It should return a list of dictionaries, where each contains the productId and a quantity (default to 1).

Hour 4: Closing the Loop (Add to Cart)
Goal: Complete the end-to-end flow by adding the found products to the user's cart.

Tasks (Finalize main.py):

Call bulk_add_to_cart: Take the list of product dictionaries from the previous step.

Make one final HTTP request to the bulk_add_to_cart tool on your MCP server, passing the list of products as the payload.

Add print statements to log the progress: "Generating shopping list...", "Found product: [Name]", "Adding items to cart...", "Successfully added items to your Kroger cart!"

Hour 5: UI & Demo Prep
Goal: Wrap your script in a simple Streamlit UI and prepare your presentation.

Tasks:

Install Streamlit: pip install streamlit

Convert main.py to a Streamlit App:

Add import streamlit as st.

Use st.title() for your app's name.

Use st.selectbox() or st.text_input() to get the user's meal choice.

Wrap your main logic inside a if st.button('Generate Plan & Add to Cart'): block.

Use st.write() and st.spinner() to display the progress messages you wrote in the previous step.

Display the final shopping list to the user with st.success().

Run the App: streamlit run main.py.

Prepare Demo Script: Rehearse a 2-minute walkthrough. Emphasize how the agent uses the MCP tools (search_products, bulk_add_to_cart) to bridge the gap between a high-level plan ("I want chicken") and a real-world action (items in a cart).

Final Advice for the Hackathon
Work in Parallel: Have one person focus on getting the Kroger MCP Server set up and authenticated (Hour 1) while another person writes the core pantry/recipe logic in Python (Hour 2).

Read the MCP README: The CupOfOwls/kroger-mcp GitHub repository README is your most important document. It details the available tools and how to use them. It even has built-in prompts and workflows you can leverage.

Don't Overcomplicate: A single, working end-to-end demo is infinitely better than a complex, half-finished one. Hardcode everything you can (pantry, recipes, location) to save time and reduce points of failure. Good luck!