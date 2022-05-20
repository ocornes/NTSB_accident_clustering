# Necessary Imports:
from bs4 import BeautifulSoup
import requests
import os
import xml

# 1: Fetching the accident ID list from XML file:
XML_filename  = 'test_55_hits.xml'  # The xml file containing all the accidents of
target_folder = 'dataset_56_hits/'
os.mkdir(target_folder)
# interest my be located in the same folder as
# this script

fd = open(XML_filename, 'r')
xml_file = fd.read()
soup = BeautifulSoup(xml_file, 'xml')  # Parses the XML file using BeautifulSoup

# Variables for the loop:
url_front = "https://app.ntsb.gov/pdfgenerator/ReportGeneratorFile.ashx?EventID="
# first part of the URL to the NTSB accident database
url_back = "&AKey=1&RType=HTML&IType=CA"
# last part of the URL to the NTSB accident database.
# The complete URL is front + accident_id + back

# 2: Go through the list of accident IDs in the XML file:
for tag in soup.findAll("ROW"):  # "ROW" is the tag that is used for every row in
    # the XML files of the NTSB
    # This loop goes through all accident IDs, fetches
    # their HTML and saves their text.
    # Debug:
    print('=========================')
    print(tag["EventId"])
    print('=========================')

    # Assemble the URL for fetching the HTML:
    event_id = tag["EventId"]
    complete_url = url_front + event_id + url_back

    # 2.C: Fetch the HTML file:
    html_raw = requests.get(url=complete_url).text
    # print(html_raw)

    # 2.D: Extract the text of interest:
    parsed_html = BeautifulSoup(html_raw, 'html.parser')

    try:
        body_tag = parsed_html.findAll("body")[0]
        main_list = body_tag.contents[0].contents
        accident_text = main_list[5].text
        # accident_text = main_list[7].text # idx=7 is "the cause of the accident determind by NTSB"
        # accident_text = parsed_html.findAll("p")[21].text

        # 2.E: Save the text of interest as a textfile with accident_id name:
        file = open(target_folder + event_id + ".txt", 'w')
        file.write(accident_text)
        file.close()

    except IndexError:
        print("No report found for the given identifiers:  " + event_id)
        continue

fd.close()  # Close the XML file
