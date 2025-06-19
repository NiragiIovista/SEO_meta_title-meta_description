import pandas as pd
import requests
import time

# === CONFIGURATION ===
TOGETHER_API_KEY = 'your_actual_api_key_here'
MODEL = 'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo'
INPUT_CSV = 'seo_output.csv'
OUTPUT_CSV = 'final_seo_output.csv'

# === FUNCTION TO CALL TOGETHER.AI TO REWRITE TEXT ===
def rewrite_with_together_api(text, purpose):
    """
    Rewrites a given meta title or description using Together.ai for more humanized and unique output.
    """
    prompt = (
        f"You are an expert SEO copywriter.\n"
        f"Rewrite the following {purpose} to sound more human, engaging, and unique. "
        f"Keep the original meaning and make sure it remains SEO-friendly.\n\n"
        f"{purpose.capitalize()}: {text}"
    )

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "max_tokens": 150,
        "temperature": 0.9,
        "top_p": 0.9,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        result = response.json()
        rewritten_text = result['choices'][0]['message']['content'].strip()

        # Extract just the text if it's prefixed like "Meta Title: ..."
        if ':' in rewritten_text:
            rewritten_text = rewritten_text.split(':', 1)[1].strip()

        return rewritten_text

    except Exception as e:
        print(f"❌ Error rewriting {purpose}: {e}")
        return text  # Fallback to original

# === MAIN FUNCTION ===
def main():
    try:
        df = pd.read_csv(INPUT_CSV)

        if 'meta_title' not in df.columns or 'meta_description' not in df.columns:
            raise ValueError("Input CSV must have 'meta_title' and 'meta_description' columns.")

        updated_titles = []
        updated_descriptions = []

        for idx, row in df.iterrows():
            print(f"🔄 Rewriting row {idx+1}/{len(df)}...")

            title = str(row['meta_title']).strip()
            desc = str(row['meta_description']).strip()

            updated_title = rewrite_with_together_api(title, "meta title")
            updated_desc = rewrite_with_together_api(desc, "meta description")

            updated_titles.append(updated_title)
            updated_descriptions.append(updated_desc)

            time.sleep(1.5)  # respect rate limit

        df['updated_meta_title'] = updated_titles
        df['updated_meta_description'] = updated_descriptions

        df.to_csv(OUTPUT_CSV, index=False)
        print(f"\n✅ Done. Final file saved as '{OUTPUT_CSV}'.")

    except Exception as e:
        print(f"❌ An error occurred: {e}")

# === RUN ===
if __name__ == "__main__":
    main()

