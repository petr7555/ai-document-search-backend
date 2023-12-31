import os
import shutil
import sys
from pathlib import Path

import pandas as pd
import requests

from ai_document_search_backend.utils.relative_path_from_file import relative_path_from_file

SOURCE_DATA_PATH = relative_path_from_file(__file__, "../../data/clean_data.csv")
DATA_DOWNLOAD_FOLDER = relative_path_from_file(__file__, "../../data/pdfs")

LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else None

if os.path.exists(DATA_DOWNLOAD_FOLDER):
    shutil.rmtree(DATA_DOWNLOAD_FOLDER)
os.makedirs(DATA_DOWNLOAD_FOLDER)

df = pd.read_csv(SOURCE_DATA_PATH)

pdf_links = df["link"].tolist()[0:LIMIT]
print(f"Number of PDFs: {len(pdf_links)}")

for i, pdf_link in enumerate(pdf_links):
    filename = pdf_link.split("/")[-1]
    print(f"Downloading {i+1}/{len(pdf_links)}: {filename}")
    res = requests.get(pdf_link)
    with open(Path(DATA_DOWNLOAD_FOLDER) / filename, "wb") as f:
        f.write(res.content)
