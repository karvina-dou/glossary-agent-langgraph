import re
import os
import json
import requests
import pandas as pd
from typing import Dict
from bs4 import BeautifulSoup
from utils import load_jsonl

def is_wikilink_valid(full_url):
    """
    Checks if a full Wikipedia URL points to an existing page.

    Args:
        full_url: The full Wikipedia URL (e.g., "https://en.wikipedia.org/wiki/Albert_Einstein").

    Returns:
        True if the page exists, False otherwise.
    """
    # Extract the page title from the URL using regex
    match = re.search(r"\/wiki\/(.+)$", full_url)
    if not match:
        return False  # Invalid URL format

    page_title = match.group(1)
    page_title = page_title.replace("_", " ")  # Replace underscores with spaces

    # Extract language code from the URL
    lang_match = re.search(r"https:\/\/([a-z]{2})\.wikipedia\.org", full_url)
    language_code = "en"  # Default to English
    if lang_match:
        language_code = lang_match.group(1)

    # Construct the API URL
    api_url = f"https://{language_code}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": page_title,
        "prop": "info",
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        for page_id, page_info in pages.items():
            if "missing" in page_info:
                return False
            else:
                return True

        return False

    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return False
    except (KeyError, TypeError) as e:
        print(f"Error parsing API response: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False


def get_wiki_table(url, i):
    # Send a GET request to the Wikipedia page
    response = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all tables on the page
    tables = soup.find_all('table', {'class': 'wikitable'})

    # Check if the ith table exists
    if i >= len(tables):
        raise ValueError(
            f"Table index {i} is out of range. There are only {len(tables)} tables on the page."
        )

    # Select the ith table
    table = tables[i]

    # Extract table headers
    headers = []
    for th in table.find_all('th'):
        headers.append(th.text.strip())

    # Extract table rows
    rows, text2url = [], {}
    for tr in table.find_all('tr'):
        cells = tr.find_all(['td', 'th'])
        if len(cells) > 0:
            row = []
            for cell in cells:
                # Check if the cell contains a link
                link = cell.find('a')
                if link and link.get('href'):
                    text2url[cell.text.strip(
                    )] = f"https://en.wikipedia.org{link.get('href')}"
                row.append(cell.text.strip())
            rows.append(row)

    # Create a DataFrame
    df = pd.DataFrame(rows[1:], columns=headers)

    return df, text2url


def get_wiki_content(url: str) -> str:
    """
    Fetches and extracts the main content from a Wikipedia page, ignoring hyperlinks, images, multi-column tables, and references.
    Bullet point style tables will be retained.
    :param url: Wikipedia page URL (string)
    :return: Extracted plain text content (string)
    """ # noqa 305
    # Fetch the Wikipedia page
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return "Error: Unable to fetch the page."

    # Parse the page content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the main content div
    content_div = soup.find("div", {"id": "mw-content-text"})

    if not content_div:
        return "Error: Could not find main content."

    # Remove unwanted elements (multi-column tables, references, images)
    for table in content_div.find_all("table", {"class": "wikitable"}):  # Remove only multi-column tables
        table.decompose()

    for element in content_div.find_all(["sup", "img"
                                         ]):  # Remove references and images
        element.decompose()

    # Extract text from paragraphs
    paragraphs = content_div.find_all("p")
    text_content = "\n".join(
        p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

    return text_content


def build_dict(table: pd.DataFrame, mapping: Dict[str, Dict]):
    def parsing(abbr):
        cln_abbr, start = '', True
        for chr in abbr:
            if chr == '(':
                start = False
            if start:
                cln_abbr += chr
        return cln_abbr

    abbr2mean, abbr2link = {}, {}
    for idx, (abbr, exp, _, _) in table.iterrows():
        if abbr not in list(mapping.keys()):
            continue
        # check if wiki link is valid
        if not is_wikilink_valid(mapping[abbr]):
            continue
        cln_abbr = parsing(abbr)
        abbr2mean[cln_abbr] = {'exp': exp, 'idx': idx}
        abbr2link[cln_abbr] = mapping[abbr]
    return abbr2mean, abbr2link


if __name__ == '__main__':
    url = "https://en.wikipedia.org/wiki/List_of_information_technology_initialisms"
    os.makedirs("./data", exist_ok=True)
    LITI, mapping = get_wiki_table(url, 0)
    a2m, a2l = build_dict(LITI, mapping)
    # for aidx, (cln_abbr, link) in enumerate(a2l.items()):
    #     wiki_content = get_wiki_content(link)
    #     with open(f'./data/wiki{str(aidx).zfill(3)}.txt', 'w') as f:
    #         f.write(wiki_content)

    desc_map = load_jsonl('./data/description.jsonl', 'description')
    with open('./data/glossary.jsonl', 'w') as jsf:
        for k, v in a2m.items():
            json_line = json.dumps({'abbreviation': k.rstrip(),
                                    'expansions': [{"expansion": v['exp'], "description": desc_map[k.rstrip()], "idx": v["idx"]}]})
            jsf.write(json_line + '\n')
