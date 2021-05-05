# Save each page of a (e.g. bioinformatics) textbook in PDF format to txt.

# installed ImageMagick
# pip install wand
# pip install pdfplumber

import pdfplumber
from os.path import abspath
from pathlib import Path
import re

#from progressbar import ProgressBar
from tqdm import tqdm
##########################
#pbar = ProgressBar()

##########################

def read_pdf(pdf_filepath):
    pdf = pdfplumber.open(abspath(pdf_filepath))
    print("Pages:", len(pdf.pages))
    return pdf

def save_page_to_text(page, title, outdir):
    filepath_out = f"{outdir}/{title}_{page.page_number}.txt"
    with open(filepath_out, 'w') as writer:
        writer.write(page.extract_text())

##########################

#pdf_filepath = "/home/marcus/Downloads/bioinformatics-data-skills.pdf"
pdf_filepath = "/home/marcus/Downloads/xiong_essential-bioinformatics.pdf"

base_path = re.match("(.*)/(.*)",pdf_filepath)[1]

title = "xiong_essential_bioinf"
outdir = f"{base_path}/pdf_to_text/{title}"

print("PDF used:",pdf_filepath)
print("Using dir:",outdir)

Path(outdir).mkdir(parents = True, exist_ok = True)

##########################

pdf = read_pdf(pdf_filepath)

pbar = tqdm(range(len(pdf.pages)-1))

for p in pbar:
    try:
        save_page_to_text(pdf.pages[p], title, outdir)
        pbar.set_description(f"Saving page {p} of {len(pdf.pages)}...")
    except:
        print("Couldn't save page",p)
        pass

print("DONE.")
pdf.close()