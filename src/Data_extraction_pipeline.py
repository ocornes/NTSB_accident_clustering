# Necessary Imports:
import sys
from bs4 import BeautifulSoup
import requests
import os
from tqdm import tqdm

default_input = 'test_55_hits.xml'  # The xml file containing all the accidents
target_folder = 'dataset/'

# Get XML input file
args = sys.argv[1:]
if len(args) == 0:
    XML_filename = default_input
else:
    XML_filename = args[0]  # First cmd arg is xml file

if not os.path.exists(XML_filename):
    # XML file does not exist
    print(f"[!] Could not find file '{XML_filename}'")
    exit(-1)

# Create output directory if it doesn't exist
if not os.path.exists(target_folder):
    os.mkdir(target_folder)
else:
    print(f"[i] Target directory '{target_folder}' already exists, not creating folder.")

# Fetching the accident ID list from XML file
fd = open(XML_filename, 'r')
xml_file = fd.read()
soup = BeautifulSoup(xml_file, 'xml')  # Parses the XML file using BeautifulSoup
tags = soup.findAll("ROW")  # "ROW" is the tag containing every 'EventId'

if len(tags) == 0:
    print(f"[!] No accident ids present in '{XML_filename}'")
    exit(0)

failed_ids = []

# URL for NTSB api
url = "https://app.ntsb.gov/pdfgenerator/ReportGeneratorFile.ashx?AKey=1&RType=HTML&IType=CA&EventID="

# Go through the list of accident IDs in the XML file
# This loop goes through all accident IDs, fetches
# their HTML and saves their text.
for tag in tqdm(tags):
    event_id = tag["EventId"]

    # Skip if already downloaded
    if os.path.exists(target_folder + event_id + '.txt'):
        continue

    # Fetch the HTML file:
    html_raw = requests.get(url=(url + event_id)).text

    # Extract the text of interest:
    parsed_html = BeautifulSoup(html_raw, 'html.parser')

    try:
        body_tag = parsed_html.findAll("body")[0]
        main_list = body_tag.contents[0].contents
        accident_text = main_list[5].text  # 5th element is the accident description

        # Save the text of interest as a textfile with accident_id name:
        file = open(target_folder + event_id + ".txt", 'w')
        file.write(accident_text)
        file.close()

    except IndexError:
        failed_ids.append(event_id)
        continue

fd.close()  # Close the XML file

print("[i] The following event_id's could not be found:")
for failed_id in failed_ids:
    print(f"\t{failed_id}")
