import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import google.generativeai as genai
import sys
import time
import os
from dotenv import load_dotenv

# --- SECURITY CONFIGURATION ---
# Load environment variables from the .env file
load_dotenv()

# Get the API Key safely
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EMAIL = "mail@example.com" # OpenAlex Polite Pool

# Check if API Key exists
if not GOOGLE_API_KEY:
    print("\n[CRITICAL ERROR] Google API Key not found!")
    print("Please create a '.env' file in this folder and add: GOOGLE_API_KEY=AIza...")
    sys.exit()

# Configure Plot Style
sns.set_theme(style="whitegrid")

def reconstruct_abstract(inverted_index):
    """
    Decodes OpenAlex's 'inverted index' format into a readable string.
    """
    if not inverted_index:
        return "[No Abstract Available]"
    
    word_index = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_index.append((pos, word))
    
    # Sort by position to reconstruct the sentence
    sorted_words = sorted(word_index, key=lambda x: x[0])
    return " ".join(word for _, word in sorted_words)

def get_user_inputs():
    """Gets search parameters from the user."""
    print("\n" + "="*60)
    print("♾️  SCHOLAR INSIGHT AI: Unlimited Bibliometric Analyzer")
    print("="*60)
    
    keyword = input("1. Enter Research Topic (e.g., recycled concrete powder): ").strip()
    # Add quotes if the user forgot them for multi-word queries
    if " " in keyword and not keyword.startswith('"'):
        keyword = f'"{keyword}"'
    
    year = input("2. Start Year (e.g., 2020): ").strip()
    year = int(year) if year.isdigit() else 2018
    
    return keyword, year

def fetch_unlimited_data(keyword, year_from):
    """
    Fetches up to 500 papers including Metadata and Abstracts from OpenAlex.
    """
    base_url = "https://api.openalex.org/works"
    
    # Filter: Search in Title/Abstract + Date + Article Type
    filter_param = (
        f"title_and_abstract.search:{keyword},"
        f"from_publication_date:{year_from}-01-01,"
        f"type:article"
    )

    # Fields to retrieve (optimized for speed)
    select_fields = "id,title,publication_year,cited_by_count,primary_location,authorships,abstract_inverted_index"

    print(f"\n[SYSTEM] Starting 'UNLIMITED' Data Mining...")
    print(f"[INFO] Target: ~500 Papers with Full Abstracts regarding {keyword}...")
    
    all_rows = []       
    unique_papers_for_ai = []  
    
    # Loop through 5 pages (100 papers per page = 500 papers)
    for page in range(1, 6): 
        params = {
            "filter": filter_param,
            "mailto": EMAIL, 
            "per_page": 100,
            "page": page,
            "sort": "cited_by_count:desc",
            "select": select_fields
        }
        
        try:
            response = requests.get(base_url, params=params)
            if response.status_code != 200:
                print(f"   -> Error accessing Page {page}. Status: {response.status_code}")
                break
                
            results = response.json().get('results', [])
            if not results:
                break
                
            print(f"   -> Page {page} downloaded successfully ({len(results)} papers).")
            
            for work in results:
                title = work.get('title', 'No Title')
                pub_year = work.get('publication_year')
                cited = work.get('cited_by_count')
                
                # 1. Decode Abstract
                raw_abstract = work.get('abstract_inverted_index')
                abstract_text = reconstruct_abstract(raw_abstract)
                
                # 2. Get Journal Name
                loc = work.get('primary_location') or {}
                source = loc.get('source') or {}
                journal = source.get('display_name', 'Unknown Journal')

                # 3. Get First Author Info (for AI Context)
                authorships = work.get('authorships', [])
                first_auth_str = "Unknown"
                if authorships:
                    first_auth = authorships[0]
                    f_name = first_auth['author']['display_name']
                    # Try to find country code
                    if first_auth.get('institutions'):
                        f_country = first_auth['institutions'][0].get('country_code', 'N/A')
                    else:
                        f_country = "N/A"
                    first_auth_str = f"{f_name} ({f_country})"

                # 4. Append to AI Context List
                unique_papers_for_ai.append(
                    f"ID: {work.get('id')}\n"
                    f"TITLE: {title}\n"
                    f"METADATA: Year {pub_year} | {cited} Citations | Journal: {journal} | Author: {first_auth_str}\n"
                    f"ABSTRACT: {abstract_text}\n" 
                    f"--------------------------------------------------"
                )

                # 5. Append to DataFrame List (for Graphs)
                # We iterate through ALL authors to get accurate country/author stats
                for authorship in authorships:
                    author_obj = authorship.get('author', {})
                    institutions = authorship.get('institutions', [])
                    
                    if institutions:
                        country_code = institutions[0].get('country_code', 'N/A')
                    else:
                        country_code = "N/A"
                    
                    all_rows.append({
                        "Author": author_obj.get('display_name', 'Unknown'),
                        "Country": country_code,
                        "Journal": journal,
                        "Year": pub_year,
                        "Citations": cited
                    })
            
            # Respect API limits
            time.sleep(0.5)

        except Exception as e:
            print(f"[ERROR] Exception occurred: {e}")
            break

    df = pd.DataFrame(all_rows)
    return df, unique_papers_for_ai

def show_graphs(df, keyword):
    """Generates visualization plots."""
    if df.empty: return
    print("\n[GRAPHICS] Generating visual insights...")
    
    # Plot 1: Top Active Countries
    plt.figure(figsize=(12, 6))
    df_country = df[df['Country'] != 'N/A']
    top_countries = df_country['Country'].value_counts().head(20) 
    
    sns.barplot(x=top_countries.values, y=top_countries.index, palette="coolwarm")
    plt.title(f"Top 20 Active Countries (Based on Author Affiliations)")
    plt.xlabel("Number of Contributions")
    plt.tight_layout()
    plt.show()

    # Plot 2: Most Productive Authors
    plt.figure(figsize=(12, 8))
    top_authors = df['Author'].value_counts().head(20) 
    
    sns.barplot(x=top_authors.values, y=top_authors.index, palette="viridis")
    plt.title(f"Top 20 Most Productive Authors")
    plt.xlabel("Number of Papers in Dataset")
    plt.tight_layout()
    plt.show()

def chat_with_gemini(unique_papers, keyword):
    """Initializes the RAG (Retrieval-Augmented Generation) session."""
    print(f"\n[AI] Initializing Gemini 2.5 Flash Model...")
    print(f"[INFO] Uploading {len(unique_papers)} full papers (titles + abstracts) to the context window.")
    
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # Merge all papers into one massive text block
        full_context = "\n".join(unique_papers)
        
        system_prompt = f"""
        You are an advanced academic research assistant utilizing RAG (Retrieval-Augmented Generation).
        Topic: '{keyword}'.
        
        I am providing you with a dataset containing approximately {len(unique_papers)} academic papers (Metadata + Abstracts).
        
        YOUR INSTRUCTIONS:
        1. Analyze the 'Abstracts' deeply to understand methodologies, materials, and results.
        2. Identify conflicting results in the literature (e.g., Paper A says X improves strength, Paper B says it reduces it).
        3. Highlight the most frequently used experimental methods.
        4. Answer specific questions about authors, countries, and collaboration opportunities.
        5. Maintain a professional, academic tone in English.
        """

        print("Uploading data to AI (This may take a few seconds)...")
        
        chat = model.start_chat(history=[
            {"role": "user", "parts": [system_prompt]},
            {"role": "model", "parts": ["Dataset received. I have analyzed the abstracts and metadata. I am ready to answer your research questions."]}
        ])

        print("\n" + "="*60)
        print("💬  INTERACTIVE CHAT MODE (English)")
        print("💡  Suggested Questions:")
        print("    - What are the most common test methods mentioned in the abstracts?")
        print("    - Are there any contradictions regarding the effect of the material on durability?")
        print("    - Which countries seem to focus on environmental impact?")
        print("="*60)

        while True:
            user_input = input("You: ")
            if user_input.lower() in ['q', 'exit', 'quit']:
                print("Exiting analysis. Goodbye!")
                break
            
            try:
                print("Gemini is thinking...", end="\r")
                response = chat.send_message(user_input)
                print(f"\nGemini: {response.text}\n")
            except Exception as e:
                print(f"\n[API Error]: {e}")

    except Exception as e:
        print(f"[Connection Error]: {e}")

def main():
    # 1. Get User Input
    keyword, year = get_user_inputs()
    
    # 2. Fetch Data (Unlimited Mode)
    df, unique_papers = fetch_unlimited_data(keyword, year)
    
    if df.empty:
        print("[System] No data found. Please check your keyword.")
        return

    # 3. Show Visualizations
    show_graphs(df, keyword)
    
    # 4. Start AI Chat
    chat_with_gemini(unique_papers, keyword)

if __name__ == "__main__":
    main()