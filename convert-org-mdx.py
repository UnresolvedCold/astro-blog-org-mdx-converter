#!/usr/bin/env python3
import re
import os

def get_frontmatter(metadata):
    frontmatter = "---\n"
    for meta in metadata:
        key, value = meta.split(" ")[0][2:], meta.split(" ")[1:]
        value = " ".join(value)
        frontmatter += f"{key}: {value}\n"
    frontmatter += "---\n"
    return frontmatter

def replace_image(match):
    url = match.group(1)
    print(f"Image URL: {url}")
    return f'<BlogImageWithContext src={{BrowserCode}} alt="" width="300" aspectRatio="16/9"/>'


def convert_org_to_mdx(org_content):
    # iterate line wise
    md_content = ""
    frontmatter = ""
    in_code_block = False
    in_result_block = False
    metadata = []

    for org_line in org_content.split("\n"):
        # convert org heading to md heading
        if org_line.startswith("*"):
            md_line = re.sub(r"^\*+", lambda x: "#" * len(x.group(0)), org_line)
            md_content += md_line + "\n"

        # Convert code block to md code block
        elif org_line.startswith("#+BEGIN_SRC") or org_line.startswith("#+begin_src"):
            md_content += "```" + org_line.split(" ")[1].split(" ")[0] + "\n"
            in_code_block = True
        elif org_line.startswith("#+END_SRC") or org_line.startswith("#+end_src"):
            md_content += "```\n"
            in_code_block = False
        elif in_code_block:
            md_content += "> "+org_line + "\n"
        # Result block    
        elif org_line.startswith("#+RESULTS:"):
            md_content += "```bash" + "\n"
            in_result_block = True
        elif in_result_block and org_line.startswith(":"):
            md_content += org_line[2:] + "\n"
        elif in_result_block and not org_line.startswith(":"):
            md_content += '```' + "\n"
            in_result_block = False
        elif org_line.startswith("#+"):
            metadata.append(org_line)
        # Normal line    
        else:
            # Bold
            org_line = re.sub(r"\*(.*?)\*", lambda x: "**" + x.group(1) + "**", org_line)
            # Italic
            org_line = re.sub(r"/(.*?)/", lambda x: "*" + x.group(1) + "*", org_line)
            # Underline
            org_line = re.sub(r"_(.*?)_", lambda x: "<u>" + x.group(1) + "</u>", org_line)
            # Strikethrough
            org_line = re.sub(r"~(.*?)~", lambda x: "~~" + x.group(1) + "~~", org_line)
            # Link
            org_line = re.sub(r"\[\[(.*?)\]\[(.*?)\]\]", lambda x: "[" + x.group(2) + "](" + x.group(1) + ")", org_line)
            # Image
            org_line = re.sub(r'\[\[([^\]]+)\]\]', replace_image, org_line)
            # Table
            org_line = re.sub(r"\|", lambda x: " | ", org_line)
            # Checkbox
            org_line = re.sub(r"\[\s\]", lambda x: "- [ ]", org_line)
            org_line = re.sub(r"\[X\]", lambda x: "- [x]", org_line)

            md_content += org_line + "\n"

    return get_frontmatter(metadata) + md_content

def convert_org_files_to_mdx(org_folder, mdx_folder):
    # Ensure mdx folder exists
    os.makedirs(mdx_folder, exist_ok=True)

    # Loop through org files in the org folder
    for org_file_name in os.listdir(org_folder):
        if org_file_name.endswith(".org"):
            org_file_path = os.path.join(org_folder, org_file_name)
            mdx_file_name = os.path.splitext(org_file_name)[0] + ".mdx"
            mdx_file_path = os.path.join(mdx_folder, mdx_file_name)

            with open(org_file_path, 'r', encoding='utf-8') as org_file:
                org_content = org_file.read()

            mdx_content = convert_org_to_mdx(org_content)

            with open(mdx_file_path, 'w', encoding='utf-8') as mdx_file:
                mdx_file.write(mdx_content)

            print(f"Converted {org_file_name} to {mdx_file_name}")
if __name__ == "__main__":
    org_file_path = "org"
    mdx_file_path = "mdx"

    convert_org_files_to_mdx(org_file_path, mdx_file_path)
    print(f"Conversion complete. MDX file saved at: {mdx_file_path}")
