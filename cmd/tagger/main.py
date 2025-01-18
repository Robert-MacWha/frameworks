import argparse
import json
import re
import os
import dotenv
import openai

# Constants
TAGS_FILE = "../../theme/tagscolors.json"
PROMPT_TAG_GENERATION = """
Analyze the provided collection of articles and generate a list of recommended tags. The tags should be highly specific, 
Zettelkasten-style, short, specific, and designed to create meaningful connections between articles. Each tag should also
be applicable for a resonably percentage of articles. If all articles share the same tag, or if only a couple articles do, 
they're unhelpful. Avoid generic tags and focus on distinct concepts, avoiding combining multiple concepts into a single tag.

Tags should be a mix of broad concepts (IE Tooling, Metrics, Best Practices, Privacy) and specific topics (IE Incident Management, IAM, Encryption).

# Steps
1. Read and analyze all articles to identify key topics, themes, and concepts.
2. Generate a list of recommended tags based on the collective content.
3. Ensure tags are unique, relevant, and focused on clarity and linking articles.
4. Avoid redundancy and over-tagging.

Output a JSON list of unique tags in order of importance or relevance.
"""

PROMPT_TAG_APPLICATION = """
Using the provided list of tags, analyze the article and assign the most relevant tags. Limit the number of tags to avoid over-tagging, with 1-3 tags for short articles and up to 5 for long articles.

# Steps
1. Analyze the article to extract its main topics, themes, and concepts.
2. Compare the extracted themes to the provided list of tags.
3. Select and apply the most relevant tags that capture the article's primary focus.

Output a JSON object with the assigned tags.
"""

MAX_TAGS_PER_ARTICLE = 5


# Helper Functions
def sanitize_article(text: str) -> str:
    """Sanitize an article by removing metadata and unnecessary text."""
    text = re.sub(r"---.*?---", "", text, flags=re.DOTALL)  # Remove YAML metadata
    text = re.sub(r"tags?: \[.*?\]\n", "", text)  # Remove inline tags
    return text.strip()


def load_articles(src_path: str) -> list[str]:
    """Load all articles from the source path."""
    articles = []
    for root, _, filenames in os.walk(src_path):
        for filename in filenames:
            if not filename.endswith(".md"):
                continue
            with open(os.path.join(root, filename), "r") as f:
                articles.append(sanitize_article(f.read()))

    return articles


def generate_tags(openai_client: openai.Client, articles: list[str]) -> list[str]:
    """Generate a list of tags for the given collection of articles."""
    combined_content = ""
    for article in articles:
        combined_content += f"```\n{article}\n```\n"

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": PROMPT_TAG_GENERATION},
            {"role": "user", "content": combined_content},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "tags_list",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "tags": {
                            "type": "array",
                            "description": "A list of tags.",
                            "items": {"type": "string"},
                        }
                    },
                    "required": ["tags"],
                    "additionalProperties": False,
                },
            },
        },
        temperature=0.7,
        max_tokens=2048,
    )
    print(response)
    try:
        tags = json.loads(response["choices"][0]["message"]["content"])
        return tags
    except Exception as e:
        print(f"Error generating tags: {e}")
        return []


def apply_tags(openai_client, articles, tags):
    """Apply generated tags to individual articles."""
    tagged_articles = []
    for article in articles:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": PROMPT_TAG_APPLICATION},
                {
                    "role": "user",
                    "content": json.dumps({"article": article, "tags": tags}),
                },
            ],
            temperature=0.7,
            max_tokens=2048,
        )
        try:
            result = json.loads(response["choices"][0]["message"]["content"])
            tagged_articles.append({"article": article, "tags": result["tags"]})
        except Exception as e:
            print(f"Error applying tags to article: {e}")
            tagged_articles.append({"article": article, "tags": []})
    return tagged_articles


def save_tags(tags: list[str], file_path: str):
    """Save the generated tags to a JSON file."""
    with open(file_path, "w") as f:
        json.dump(tags, f, indent=2)


def main():
    dotenv.load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    src_path = os.getenv("SRC_PATH", "src/")

    # Load articles
    articles = load_articles(src_path)

    # Initialize OpenAI client
    openai_client = openai.Client(api_key=openai_api_key)

    # Generate tags from all articles
    tags = generate_tags(openai_client, articles)
    print(f"Generated Tags: {tags}")

    # Save tags to a file
    save_tags(tags, TAGS_FILE)

    # Apply tags to individual articles
    # tagged_articles = apply_tags(openai_client, articles, tags)

    # # Output tagged articles
    # for tagged in tagged_articles:
    #     print(f"Article Tags: {tagged['tags']}")


if __name__ == "__main__":
    main()
