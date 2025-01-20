# Migrate.py is a script that migrates the src directory's wiki from the current mdbook format to
# a decap-cms compatible format.  It re-structures the directories and adds frontmatter yaml.

import os
import re

def main():
    # Load summary.md file
    summary = open("src/SUMMARY.md", "r")

    # Iterate over all files in summary.md, load the file, and process it.
    i = 0
    for line in summary:
        # Extract file path with regex
        match = re.search(r'\[(.*?)\]\((.*?)\)', line)
        if not match:
            continue

        title = match.group(1)
        path = os.path.join("./src", match.group(2))
        path = os.path.normpath(path)

        # Strip existing metadata from file
        file = open(path, "r")

        # Remove title
        lines = file.readlines()
        if lines[0].startswith("---"):
            break # Has frontmatter, assume it's already been processed
            
        if lines[0].startswith("# "):
            lines.pop(0)
        file.close()

        # Extract tags
        tags = []
        for line in lines:
            if line.startswith("tag: ["):
                tags = line.replace("tag: [", "").replace("]", "").split(", ")
                lines.remove(line)
                break

        # Add frontmatter
        frontmatter = "---\n"
        frontmatter += f"title: {title}\n"
        frontmatter += f"tags:\n"
        for tag in tags:
            frontmatter += f"  - {tag}\n"
        frontmatter += f"sidebar_position: {i * 10}\n"
        frontmatter += "---\n"
        i += 1

        # Create new dir
        filename = os.path.basename(path).replace(".md", "")
        new_file = os.path.join("./new_src", os.path.dirname(path), filename, "index.md")
        if filename == "README" or filename == "index":
            new_file = os.path.join("./new_src", os.path.dirname(path), "index.md")

        os.makedirs(os.path.dirname(new_file), exist_ok=True)

        # Write the updated file
        file = open(new_file, "w+")
        file.write(frontmatter)
        for line in lines:
            file.write(line)
        file.close()

if __name__ == "__main__":
    main()