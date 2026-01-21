"""
OpenAlex Data Analyzer (Self-Installing)
========================================

Description:
  This script analyzes academic paper data from OpenAlex.
  It automatically creates a 'results' folder in the script's directory,
  installs missing dependencies, and generates insights.

Usage:
  1. Ensure 'requirements.txt' is in the same folder.
  2. Run this script: python main.py
"""

import sys
import subprocess
import os
import importlib

# --- Dependency Management ---

def install_requirements():
    """
    Checks for requirements.txt and installs dependencies via pip.
    """
    req_file = "requirements.txt"
    if not os.path.exists(req_file):
        print(f"Error: '{req_file}' not found. Cannot install dependencies.")
        sys.exit(1)

    print(f"Installing dependencies from {req_file}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
        print("Dependencies installed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        sys.exit(1)

def check_and_import_dependencies():
    """
    Tries to import required libraries. If they fail, triggers installation.
    """
    required_libs = ['requests', 'pandas', 'matplotlib', 'seaborn', 'pycountry']
    
    missing_libs = []
    for lib in required_libs:
        if importlib.util.find_spec(lib) is None:
            missing_libs.append(lib)
    
    if missing_libs:
        print(f"Missing libraries detected: {', '.join(missing_libs)}")
        install_requirements()
    else:
        # Check passed implicitly
        pass

# --- Perform Dependency Check Before Main Imports ---
check_and_import_dependencies()

# --- Main Imports (After Check) ---
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pycountry

# --- Configuration ---
# Please replace with your actual email for the OpenAlex Polite Pool
EMAIL = "your_email@example.com" 

def reconstruct_abstract(inverted_index):
    """
    Reconstructs the full abstract text from OpenAlex's inverted index format.
    """
    if not inverted_index:
        return ""
    word_index = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_index.append((pos, word))
    word_index.sort()
    return " ".join([word for _, word in word_index])

def get_country_name(code):
    """
    Converts a 2-letter ISO country code to its full English name.
    """
    if not code: return "Unknown"
    try:
        return pycountry.countries.get(alpha_2=code).name
    except:
        return code

def fetch_openalex_data():
    print("--- OpenAlex Data Fetcher ---")
    
    # 1. Collect User Inputs
    keywords = input("Keyword(s) (e.g., 'generative ai'): ")
    start_year = input("Start Year (YYYY): ")
    end_year = input("End Year (YYYY): ")
    
    inc_conf = input("Include Conference Papers? (y/n): ").lower()
    inc_books = input("Include Books/Book Chapters? (y/n): ").lower()
    
    # --- AUTOMATIC DIRECTORY SETUP ---
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Define 'results' folder path relative to the script
    output_dir = os.path.join(script_dir, "results")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"\nCreated output directory: {output_dir}")
    else:
        print(f"\nResults will be saved to: {output_dir}")
    # ----------------------------------

    # 2. Build API Query Filters
    base_url = "https://api.openalex.org/works"
    filters = [f"publication_year:{start_year}-{end_year}"]
    
    types = ["article"]
    if inc_conf == 'y':
        types.append("proceedings-article")
    if inc_books == 'y':
        types.extend(["book", "book-chapter"])
    
    type_filter = "|".join(types)
    filters.append(f"type:{type_filter}")
    
    params = {
        "search": keywords,
        "filter": ",".join(filters),
        "per_page": 200,
        "mailto": EMAIL
    }

    print(f"Fetching data from OpenAlex... (Included types: {types})")
    
    works_data = []
    cursor = "*"
    
    while True:
        params["cursor"] = cursor
        try:
            r = requests.get(base_url, params=params)
            r.raise_for_status()
            data = r.json()
            
            results = data.get('results', [])
            if not results:
                break
                
            for work in results:
                # Metadata extraction
                title = work.get('title', '')
                pub_year = work.get('publication_year')
                citations = work.get('cited_by_count', 0)
                
                source_name = "Unknown"
                if work.get('primary_location') and work['primary_location'].get('source'):
                    source_name = work['primary_location']['source']['display_name']
                
                authors_list = []
                countries_list = []
                institutions_list = []
                
                for authorship in work.get('authorships', []):
                    author_name = authorship['author']['display_name']
                    authors_list.append(author_name)
                    
                    for inst in authorship.get('institutions', []):
                        institutions_list.append(inst['display_name'])
                        cc = inst.get('country_code')
                        if cc:
                            countries_list.append(get_country_name(cc))
                
                abstract_text = reconstruct_abstract(work.get('abstract_inverted_index'))
                concepts = [c['display_name'] for c in work.get('concepts', [])]
                
                works_data.append({
                    'title': title,
                    'publication_year': pub_year,
                    'cited_by_count': citations,
                    'source_name': source_name,
                    'authors': authors_list,
                    'authors_str': "; ".join(authors_list),
                    'institutions': "; ".join(list(set(institutions_list))),
                    'countries': countries_list,
                    'countries_str': "; ".join(list(set(countries_list))),
                    'abstract': abstract_text,
                    'keywords': "; ".join(concepts)
                })
            
            cursor = data['meta']['next_cursor']
            print(f"Fetched {len(works_data)} records so far...")
            
            if len(works_data) >= 2000:
                print("Demo limit of 2000 records reached.")
                break
                
        except Exception as e:
            print(f"An error occurred during fetching: {e}")
            break

    # 3. Export Data
    df = pd.DataFrame(works_data)
    if df.empty:
        print("No papers found matching these parameters.")
        return

    df_export = df.drop(columns=['authors', 'countries']) 
    csv_path = os.path.join(output_dir, "openalex_papers.csv")
    df_export.to_csv(csv_path, index=False)
    print(f"\nData successfully saved to: {csv_path}")

    # 4. Generate Visualizations
    generate_plots(df, output_dir)

def generate_plots(df, output_dir):
    sns.set_theme(style="whitegrid")
    
    # 1. Publication Trend
    plt.figure(figsize=(10, 6))
    year_counts = df['publication_year'].value_counts().sort_index()
    if not year_counts.empty:
        sns.lineplot(x=year_counts.index, y=year_counts.values, marker="o")
        plt.title("Publication Trend (Count vs Year)")
        plt.xlabel("Year")
        plt.ylabel("Number of Publications")
        plt.savefig(os.path.join(output_dir, "1_publication_trend.png"))
        plt.show()

    # 2. Top Active Countries
    all_countries = [c for sublist in df['countries'] for c in sublist]
    if all_countries:
        country_counts = pd.Series(all_countries).value_counts().head(10)
        plt.figure(figsize=(12, 6))
        sns.barplot(x=country_counts.values, y=country_counts.index, hue=country_counts.index, palette="viridis", legend=False)
        plt.title("Top 10 Active Countries")
        plt.xlabel("Number of Affiliated Papers")
        plt.savefig(os.path.join(output_dir, "2_top_countries.png"))
        plt.show()

    # 3. Top Researchers
    all_authors = [a for sublist in df['authors'] for a in sublist]
    if all_authors:
        author_counts = pd.Series(all_authors).value_counts().head(10)
        plt.figure(figsize=(12, 6))
        sns.barplot(x=author_counts.values, y=author_counts.index, hue=author_counts.index, palette="magma", legend=False)
        plt.title("Top 10 Researchers")
        plt.xlabel("Number of Papers in Dataset")
        plt.savefig(os.path.join(output_dir, "3_top_researchers.png"))
        plt.show()

    # 4. Top Journals
    journal_counts = df['source_name'].value_counts().head(10)
    if not journal_counts.empty:
        plt.figure(figsize=(12, 6))
        sns.barplot(x=journal_counts.values, y=journal_counts.index, hue=journal_counts.index, palette="rocket", legend=False)
        plt.title("Top 10 Journals / Sources")
        plt.xlabel("Count")
        plt.savefig(os.path.join(output_dir, "4_top_journals.png"))
        plt.show()

    # 5. Impact Timeline (Scatter)
    plt.figure(figsize=(12, 7))
    sns.scatterplot(
        data=df,
        x="publication_year",
        y="cited_by_count",
        size="cited_by_count",
        sizes=(20, 500),
        alpha=0.7,
        color="purple",         
        legend=False            
    )
    plt.title("Impact Timeline (Individual Paper Citations by Year)")
    plt.xlabel("Publication Year")
    plt.ylabel("Citations")
    plt.savefig(os.path.join(output_dir, "5_impact_timeline_scatter.png"))
    plt.show()

    # 6. Heatmap: Top Countries vs Years
    country_year_data = []
    for index, row in df.iterrows():
        year = row['publication_year']
        if year and row['countries']:
            for country in row['countries']:
                country_year_data.append({'year': year, 'country': country})
    
    if country_year_data:
        df_cy = pd.DataFrame(country_year_data)
        top_countries = df_cy['country'].value_counts().head(10).index
        df_cy_filtered = df_cy[df_cy['country'].isin(top_countries)]
        heatmap_data = df_cy_filtered.groupby(['country', 'year']).size().unstack(fill_value=0)

        plt.figure(figsize=(14, 8))
        sns.heatmap(heatmap_data, cmap="YlGnBu", linewidths=.5, annot=True, fmt="d", cbar_kws={'label': 'Number of Publications'})
        plt.title("Heatmap: Publication Activity by Top Countries over Years")
        plt.ylabel("Country")
        plt.xlabel("Year")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "6_country_year_heatmap.png"))
        plt.show()
    else:
        print("\nNot enough country/year data to generate heatmap.")

    print(f"\nAll plots have been generated and saved to: {output_dir}")

if __name__ == "__main__":
    fetch_openalex_data()