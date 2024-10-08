from transformers import pipeline
import argparse
import json
import torch
import re

# roberta and bart don't seem to perform that well on zero-shot classification.
# ChatGPT does a good job, so it's clearly just a scale issue, but I haven't
# yet found a model that can be run locally and produces good results.
#
# Attempted so far: facebook/bart-large-mnli, roberta-large-mnli, mDeBERTa-v3-base-xnli-multilingual-nli-2mil7

TAGS_FILE = "../../theme/tagscolors.json"
SCORE_TRESHOLD = 0.6

def get_tags():
    with open(TAGS_FILE, 'r') as f:
        raw = json.load(f)
        return list(raw.keys())

def main():
    parser = argparse.ArgumentParser(description="Tagger")
    parser.add_argument("file", type=str, help="Path to the file to be tagged")

    args = parser.parse_args()

    file_content = ""
    with open(args.file, 'r') as f:
        file_content = f.read()

    # remove existing tags since it messes with the classifier
    file_content = re.sub(r'^tag: \[.*\]\n?', '', file_content, flags=re.MULTILINE)

    print("Loaded File")

    tags = get_tags()
    print("Loaded Tags")

    print("Parsing Keywords...")
    device = 0 if torch.cuda.is_available() else -1
    classifier = pipeline("zero-shot-classification", model="roberta-large-mnli", device=device)
    result = classifier(file_content, tags, multi_label=True)
    print("Parsed Keywords")

    scored_tags = list(zip(result['labels'], result['scores']))
    scored_tags = sorted(scored_tags, key=lambda x: x[1])
    # scored_tags = filter(lambda x: x[1] > SCORE_TRESHOLD, scored_tags)
    for tag, score in scored_tags:
        score = round(score, 2)
        print(f"{tag}: {score}")
            

if __name__ == "__main__":
    main()