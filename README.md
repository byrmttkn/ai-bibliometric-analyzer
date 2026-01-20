This tool performs advanced bibliometric analysis using OpenAlex (for data mining) and Google Gemini 2.5 Flash (for AI-powered insights). It fetches hundreds of academic papers, visualizes trends, and allows you to "chat" with the research data.

FEATURES

Unlimited Mode: Fetches up to 500+ papers with full abstracts.

Deep Analysis: Decodes OpenAlex inverted abstracts into readable text.

Visualizations: Generates graphs for Top Countries, Active Authors, and more.

RAG Chat: Uses Retrieval-Augmented Generation to answer questions like "What are the conflicting results in this field?".

INSTALLATION & SETUP

Clone the Repository Download this project to your local machine.

Install Dependencies Open your terminal/command prompt and run: pip install -r requirements.txt

API Key Setup (Important!) You need a Google Gemini API Key to run the AI features.

Get a free key from Google AI Studio (https://aistudio.google.com/).

Create a new file named .env in the project folder.

Add your key inside it like this: GOOGLE_API_KEY=AIzaSy... (Paste your key here) (Do not share your .env file with anyone!)

USAGE Run the main script: python main.py Follow the on-screen prompts to enter your research topic and start year.

EXAMPLE OUTPUT The tool will display:

Country Distribution Graph

Top Authors Chart

Interactive AI Chat Session

Project created for Academic Research Collaboration.
