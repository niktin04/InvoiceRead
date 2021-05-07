import os
import csv
import re

import pdfplumber

INVOICES_DIRECTORY = os.getcwd() + "/Invoices/"


def analyse_pdf(pdf_file_path):
    # Opening pdf file with pdfplumber
    with pdfplumber.open(pdf_file_path) as pdf:

        # PDF properties
        metadata = pdf.metadata
        pages = pdf.pages

        # Analysing page data
        for page in pages:

            # Page properties: Basic
            page_number = page.page_number
            page_width = page.width
            page_height = page.height

            # Page properties: Visible lines
            page_lines = page.lines

            print(page.extract_text())

for root, directories, files in os.walk(INVOICES_DIRECTORY):

    # Current working directory and count of files and folders
    print("----")
    print(f"Current working directory: {root}")
    print(f"{len(directories)} folder(s) found, {len(files)} file(s) found")
    print("----")

    # Looping through files and analysing pdf files
    for file in files:
        if file.endswith(".pdf"):
            # Creating file path
            file_path = os.path.join(root, file)
            print(f"Analysing file: {file_path}")

            # Analysing pdf file
            analyse_pdf(file_path)
