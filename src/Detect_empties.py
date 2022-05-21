import os
from tqdm import tqdm

DATASET_DIR = "./dataset/"
OUTPUT = "empty_hits.xml"
EMPTY_SIZE = 2

file = open(OUTPUT, "w+")
file.write("<DATA>\n<ROWS>\n")

for report in tqdm(os.listdir(DATASET_DIR)):
    if os.path.getsize(DATASET_DIR + report) == EMPTY_SIZE:
        file.write(f"<ROW EventId=\"{report}\"/>\n")

file.write("</ROWS>\n</DATA>\n")
file.close()
