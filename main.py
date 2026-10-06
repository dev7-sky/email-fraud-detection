import os

from parser.mail_parser import parse_mbox
from viewer.html_generator import create_viewer
import webbrowser
# from REPORT.export_report import generate_csv



path = input("File name: ")

output_folder = "outputs"

os.makedirs(output_folder, exist_ok=True)

emails, total = parse_mbox(path, output_folder)

# generate_csv(emails)

create_viewer(emails, total, output_folder)

print("Completed Successfully!")

webbrowser.open(os.path.abspath(os.path.join(output_folder,"index.html")))