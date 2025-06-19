#meta_title and meta description using AI 
import pandas as pd
import requests
import time
import nltk
import re
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# === NLTK Data Download (Run once) ===
try:
    nltk.data.find('corpora/wordnet')
    nltk.data.find('taggers/averaged_perceptron_tagger')
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    print("Downloading NLTK data... This may take a moment.")
    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('omw-1.4')
except Exception as e:
    print(f"Unexpected error during NLTK data check/download: {e}")

# === CONFIGURATION ===
TOGETHER_API_KEY = 'd6d20ea306517e42efc74d921fc9bd88dcc751ffa9c16e8c9d402eda2c3f4288'
MODEL = 'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo'
INPUT_CSV = 'keywords.csv'
OUTPUT_CSV = 'seo_output.csv'
CHAR_LIMIT_TITLE = 60
CHAR_LIMIT_DESC = 160

# === SMART TRUNCATION (UPDATED) ===
def smart_truncate(text, max_length):
    """
    Truncates text at the last full sentence within max_length.
    Falls back to nearest word boundary if needed.
    """
    if len(text) <= max_length:
        return text.strip()

    # Try truncating at full sentence boundaries
    sentences = re.split(r'(?<=[.!?]) +', text)
    truncated = ""
    for sentence in sentences:
        if len(truncated) + len(sentence) <= max_length:
            truncated += sentence + " "
        else:
            break

    if truncated.strip():
        return truncated.strip()

    # Fallback: truncate at word boundary
    return text[:max_length].rsplit(' ', 1)[0].strip()

# === POST-PROCESSING PLACEHOLDER ===
def post_process_with_nltk(text):
    return text  # Currently returns as-is

# === TOGETHER.AI CALL FUNCTION ===
def generate_meta(keyword, page_type, features, audience):
    features_list = features.split('|') if isinstance(features, str) else []
    features_str = ', '.join(features_list) if features_list else 'N/A'
    audience_str = audience if isinstance(audience, str) and audience.strip() else 'General'

    prompt = (
        f"You are an expert SEO copywriter known for crafting natural, engaging, and human-like meta descriptions and titles.\n"
        f"Generate a compelling meta title (max {CHAR_LIMIT_TITLE} characters) and a captivating meta description (max {CHAR_LIMIT_DESC} characters) "
        f"for a {page_type} page using the primary keyword '{keyword}'.\n"
        f"Incorporate features: {features_str}.\n"
        f"Target audience: {audience_str}.\n"
        f"The description must end with a complete sentence and be human-readable and SEO-friendly.\n\n"
        f"Respond exactly in this format:\n"
        f"Title: <your title>\n"
        f"Description: <your description>"
    )

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "max_tokens": 250,
        "temperature": 0.9,
        "top_p": 0.9,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = None
    try:
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        output = response.json()
        content = output['choices'][0]['message']['content']

        # Debug raw response (can comment out)
        # print("Raw model response:\n", content)

        title = ""
        description = ""
        for line in content.split('\n'):
            if line.lower().startswith("title:"):
                title = line.split(":", 1)[1].strip()
            elif line.lower().startswith("description:"):
                description = line.split(":", 1)[1].strip()

        if not description:
            print(f"⚠️ Description missing for keyword: '{keyword}'")

        processed_title = post_process_with_nltk(title)
        processed_description = post_process_with_nltk(description)

        return smart_truncate(processed_title, CHAR_LIMIT_TITLE), smart_truncate(processed_description, CHAR_LIMIT_DESC)

    except requests.exceptions.RequestException as e:
        print(f"❌ API Request Error for keyword '{keyword}': {e}")
        if response is not None:
            print("Response status code:", response.status_code)
            print("Response content:", response.text)
        return "", ""
    except KeyError as e:
        print(f"❌ Parsing error: missing key {e} for keyword '{keyword}'.")
        if response is not None:
            print("Raw response content:", response.text)
        return "", ""
    except Exception as e:
        print(f"❌ Unexpected error for keyword '{keyword}': {e}")
        return "", ""

# === MAIN ===
def main():
    try:
        df = pd.read_csv(INPUT_CSV)
        df.columns = df.columns.str.strip()

        if 'keyword' not in df.columns:
            raise ValueError(f"CSV must contain a 'keyword' column. Found: {', '.join(df.columns)}")

        for col in ['page_type', 'features', 'audience']:
            if col not in df.columns:
                print(f"Column '{col}' not found. Filling with defaults.")
                df[col] = ''

        titles, descriptions = [], []

        for idx, row in df.iterrows():
            keyword = row['keyword']
            if not isinstance(keyword, str) or not keyword.strip():
                print(f"Skipping row {idx+1} due to empty keyword.")
                titles.append("")
                descriptions.append("")
                continue

            print(f"🔄 Processing {idx+1}/{len(df)}: {keyword}")

            title, desc = generate_meta(
                keyword=keyword,
                page_type=row.get('page_type', 'product'),
                features=row.get('features', ''),
                audience=row.get('audience', '')
            )

            titles.append(title)
            descriptions.append(desc)
            time.sleep(1.5)

        df['meta_title'] = titles
        df['meta_description'] = descriptions
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"\n✅ Done. SEO metadata saved to: {OUTPUT_CSV}")

    except FileNotFoundError:
        print(f"❌ File '{INPUT_CSV}' not found.")
    except pd.errors.EmptyDataError:
        print(f"❌ File '{INPUT_CSV}' is empty.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

