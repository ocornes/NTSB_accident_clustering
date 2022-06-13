# Necessary Imports:
import sys
from bs4 import BeautifulSoup
import requests
import os
from tqdm import tqdm

from NTSBUtils import output_errors, parse_findings

NO_REPORT = 'No report found for the given identifiers.'
ACCIDENT_TO_BE_ = "The National Transportation Safety Board determines the probable cause(s) of this accident to be:"
INCIDENT_TO_BE_ = "The National Transportation Safety Board determines the probable cause(s) of this incident to be:"

default_input = 'test_55_hits.xml'  # The xml file containing all the accidents
target_folder = 'dataset/'
overwrite = True
error_file = 'error.xml'

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
cause_malformed_ids = []  # probable cause doesn't start with correct header
findings_malformed_ids = []  # findings table is missing
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
    try:
        html_raw = requests.get(url=(url + event_id)).text
    except Exception as e:
        unknown_errors.append((event_id, e))
        continue

    # Check for 404
    if html_raw == NO_REPORT:
        false_ids.append(event_id)
        continue

    # Extract the text of interest:
    parsed_html = BeautifulSoup(html_raw, 'html.parser')
    try:
        body_tag = parsed_html.findAll("body")[0]
        main_section = body_tag.contents[0].contents

        report_elements = []
        for report_tag in main_section[4:]:  # First 4 elements are report header
            # If tag is a section header or is not empty
            if report_tag.name == 'h2' or \
                    report_tag.text != '' and report_tag.text != ' ':
                report_elements.append(report_tag)
                # If tag is table, it's the Findings section
                if report_tag.name == 'table':
                    break

        # The report_elements should contain:
        # Analysis header, Analysis section,
        # Probable Cause header, Probable Cause section,
        # and Findings section
        if len(report_elements) != 5:
            malformed_ids.append(event_id)
            continue

        # Get Analysis section
        analysis_text = report_elements[1].text

        # Get Probable Cause section
        probable_cause_text = report_elements[3].text
        # Check (and remove) standard preamble
        if not probable_cause_text.startswith(ACCIDENT_TO_BE_) and \
                not probable_cause_text.startswith(INCIDENT_TO_BE_):
            # malformed report, fix manually
            cause_malformed_ids.append(event_id)
            continue
        probable_cause_text = probable_cause_text[len(ACCIDENT_TO_BE_):]

        # Parse Findings section (in table form)
        findings_table = report_elements[4]
        findings_element = findings_table.contents[1].contents[0].contents[1]
        findings = []
        for f in findings_element.contents:
            if f.text != '':
                findings.append(f.text)

        findings_text = parse_findings(findings)
        if findings_text == '':
            # no findings, error must have happened
            findings_malformed_ids.append(event_id)
            continue

        # Save the text of interest as a textfile with accident_id name:
        file = open(target_folder + event_id + ".txt", 'w')
        file.write(analysis_text)
        file.write('\n')
        file.write(probable_cause_text)
        file.write('\n')
        file.write(findings_text)
        file.close()

    except Exception as e:
        unknown_errors.append((event_id, e))
        continue

fd.close()  # Close the XML file

output_errors(error_file=error_file,
              unknown=unknown_errors,
              malformed=malformed_ids,
              cause_malformed=cause_malformed_ids,
              findings_malformed=findings_malformed_ids,
              not_found=false_ids)
