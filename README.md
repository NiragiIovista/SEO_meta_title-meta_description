# SEO_meta_title-meta_description
This project consists of two Python scripts designed to generate and rewrite SEO-optimized meta titles and descriptions using LLMs via the Together.ai API.

✅ Automatically generates high-quality SEO meta titles and descriptions using AI.

✨ Enhances the generated metadata to make it more human-like, engaging, and unique.

🧠 Uses advanced models like Meta-LLaMA-3.1-8B-Instruct-Turbo.

📊 Works with CSV files for batch processing.


🧠 Script 1: generate_meta.py

Purpose:
Generates SEO-friendly meta titles and descriptions using LLMs.

Input:
keywords.csv

Output:
seo_output.csv with added meta_title and meta_description columns.

✨ Script 2: rewrite_meta.py

Purpose:
Refines and rewrites the generated meta titles/descriptions to sound more human, engaging, and unique — without losing SEO value.

Input:
seo_output.csv (from Script 1)

Output:
final_seo_output0.csv with two new columns:
updated_meta_title and updated_meta_description

🛠️ Setup Instructions

1. Clone the repository

    bash

    git clone https://github.com/your-username/seo-meta-generator.git
    cd seo-meta-generator

2. Install dependencies

  bash
  pip install pandas requests nltk

3. Run NLTK Downloads (automatically handled, but can be manually triggered)

    import nltk

    nltk.download('punkt')

    nltk.download('wordnet')

    nltk.download('averaged_perceptron_tagger')

    nltk.download('omw-1.4')


4. Add your API Key

    TOGETHER_API_KEY = 'your_actual_api_key_here'

