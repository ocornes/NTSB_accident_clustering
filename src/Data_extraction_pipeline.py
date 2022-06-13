# Necessary Imports:
import sys
from bs4 import BeautifulSoup
import requests
import os
from tqdm import tqdm

from Output_errors import output_errors

default_input = 'test_55_hits.xml'  # The xml file containing all the accidents
target_folder = 'dataset/'
overwrite = True
error_file = ''

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

false_ids = []  # 404 error, report doesn't exist
malformed_ids = []  # report has blank sections in expected positions
unknown_errors = []  # ids that failed for unknown reasons

# URL for NTSB api
url = "https://app.ntsb.gov/pdfgenerator/ReportGeneratorFile.ashx?AKey=1&RType=HTML&IType=CA&EventID="

# Go through the list of accident IDs in the XML file
# This loop goes through all accident IDs, fetches
# their HTML and saves their text.
for tag in tqdm(tags):
    event_id = tag["EventId"]

    # Skip if already downloaded
    if not overwrite and os.path.exists(target_folder + event_id + '.txt'):
        continue

    # Fetch the HTML file:
    html_raw = requests.get(url=(url + event_id)).text

    # Check for 404
    if html_raw == 'No report found for the given identifiers.':
        false_ids.append(event_id)
        continue

    # Extract the text of interest:
    parsed_html = BeautifulSoup(html_raw, 'html.parser')

    try:
        body_tag = parsed_html.findAll("body")[0]
        main_list = body_tag.contents[0].contents
        analysis_text = main_list[5].text  # 5th element is the accident description

        if analysis_text == ' ':
            # malformed report, fix manually
            malformed_ids.append(event_id)
            continue

        # Save the text of interest as a textfile with accident_id name:
        file = open(target_folder + event_id + ".txt", 'w')
        file.write(analysis_text)
        file.close()

    except Exception as e:
        unknown_errors.append((event_id, e))
        continue

fd.close()  # Close the XML file

output_errors(error_file=error_file,
              unknown=unknown_errors,
              malformed=malformed_ids,
              not_found=false_ids)
