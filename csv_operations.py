import os
import csv

csv_files_path = os.path.abspath("./csv")


def get_all_csv_files():
    for dirpath, _, filenames in os.walk(csv_files_path):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


def delete_downloaded_bundle_id(csv_file, bundle_id):
    rows_keep = []
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        print(bundle_id)
        for row in reader:
            print(row)
        try:
            rows_keep = [row for row in reader if not row[5].__contains__(bundle_id)]
        except:
            return

    with open(csv_file, "w", newline="", encoding="utf-8") as wrt:
        writer = csv.writer(wrt)
        for row in rows_keep:
            writer.writerow(row)


def get_bundle_ids(csv_file):
    ids = []
    with open(csv_file, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ids.append(row["bundle id"].split("/")[3])

    return ids
