# OpenAlex Academic Data Analyzer 📊

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![OpenAlex](https://img.shields.io/badge/Data-OpenAlex_API-orange)

A powerful, self-installing Python tool to fetch, analyze, and visualize academic research data using the **OpenAlex API**. 

This tool automates the literature review process by extracting metadata (titles, abstracts, authors, countries) and generating insightful visualizations—ready for export to AI tools (like Gemini/ChatGPT) or inclusion in reports.

## 🚀 Features

* **Automated Data Fetching:** Retrieves papers based on keywords, date ranges, and document types.
* **Smart Metadata Extraction:** Reconstructs abstracts from inverted indexes, resolves country codes to full names, and aggregates author data.
* **Self-Healing Dependencies:** Automatically checks and installs required libraries (`requirements.txt`) upon first run.
* **Machine-Readable Output:** Exports a clean `.csv` file perfect for further analysis with LLMs.
* **6 Automatic Visualizations:**
    1.  📈 **Publication Trend:** Line chart of activity over time.
    2.  🌍 **Top Active Countries:** Bar chart of global contribution.
    3.  👩‍🔬 **Top Researchers:** Identification of leading authors.
    4.  📰 **Top Journals:** Most frequent publication venues.
    5.  🟣 **Impact Timeline:** Bubble/Scatter plot (Citations vs. Year).
    6.  🔥 **Activity Heatmap:** Intensity of top countries over years.

## 📦 Installation

This script comes with a **self-installation mechanism**. You don't need to manually install libraries if you have Python and `pip` installed.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/openalex-analyzer.git
    cd openalex-analyzer
    ```

2.  **Run the script:**
    ```bash
    python main.py
    ```
    *On the first run, the script will automatically detect missing libraries (pandas, seaborn, etc.) and install them from `requirements.txt`.*

## ⚙️ Configuration

Open `main.py` and update the `EMAIL` variable. 
This adds you to the [OpenAlex Polite Pool](https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication), ensuring much faster response times.

```python
# In main.py
EMAIL = "your_email@example.com" 
```

## 🖥️ Usage

Run the script and follow the interactive prompts. The script will automatically create a `results` folder in the same directory.

```text
--- OpenAlex Data Fetcher ---
Keyword(s): "generative ai" OR "large language models"
Start Year (YYYY): 2020
End Year (YYYY): 2024
Include Conference Papers? (y/n): y
Include Books/Book Chapters? (y/n): n
```

### 💡 Input Guide & Search Tips

Here is how to answer the prompts for the best results:

#### 1. Keyword(s)
This input supports the full OpenAlex search syntax.
* **Simple Search:** `machine learning`
    * *Effect:* Finds papers containing both "machine" AND "learning".
* **Exact Phrase:** `"generative ai"`
    * *Effect:* Finds papers with this exact phrase. **Use double quotes (") for phrases.**
* **Boolean Logic (OR):** `cancer OR tumor OR oncology`
    * *Effect:* Finds papers containing *at least one* of these terms.
* **Complex Logic:** `("deep learning" OR "neural networks") AND vision`
    * *Effect:* Finds papers about vision that also mention deep learning or neural networks.
* **Grouping:** Use parentheses `()` to group logic as shown above.

#### 2. Start / End Year
Enter the year as a 4-digit number (e.g., `2023`).
* *Note:* The range is inclusive (e.g., 2020-2022 includes 2020, 2021, and 2022).

#### 3. Include Conference Papers / Books (y/n)
* Type `y` (yes) to include these document types in your dataset.
* Type `n` (no) to exclude them and strictly stick to journal articles.

## 📊 Visualizations Generated

The script generates high-resolution `.png` files in the `results/` directory:

| Visualization | Description |
| :--- | :--- |
| **1_publication_trend.png** | Shows the growth or decline of the topic over the selected years. |
| **2_top_countries.png** | Visualizes which countries are leading the research. |
| **3_top_researchers.png** | Lists the most prolific authors in the dataset. |
| **4_top_journals.png** | Shows the top sources (journals/conferences). |
| **5_impact_timeline_scatter.png** | A scatter plot where bubble size represents citation count, showing high-impact papers. |
| **6_country_year_heatmap.png** | A heatmap showing publication intensity of the top 10 countries across years. |

## 📂 Output Structure

After running, your folder will look like this:

```
├── main.py
├── requirements.txt
└── results/
    ├── openalex_papers.csv       # The dataset (upload this to Gemini/ChatGPT!)
    ├── 1_publication_trend.png
    ├── 2_top_countries.png
    ├── ...
    └── 6_country_year_heatmap.png
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---
*Data provided by [OpenAlex](https://openalex.org).*
