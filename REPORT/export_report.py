import csv
import os

def generate_csv(email_list, output_folder="outputs"):

    report_path = os.path.join(output_folder, "report.csv")

    with open(report_path, "w", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        writer.writerow([
            "ID",
            "Subject",
            "From",
            "To",
            "Date",
            "Labels",
            "Attachments"
        ])

        for email in email_list:

            writer.writerow([
                email["id"],
                email["subject"],
                email["from"],
                email["to"],
                email["date"],
                email["labels"],
                ", ".join(email["attachments"])
            ])

    print("CSV Report Generated Successfully.")