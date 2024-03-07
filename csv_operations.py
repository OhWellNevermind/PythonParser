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
        csv_list = list(reader)
        bundle_index = csv_list[0].index("bundle id")
        rows_keep = []
        try:
            for row in csv_list:
                if (
                    row[bundle_index] == "bundle id"
                    or row[bundle_index].split("/")[3] != bundle_id
                ):
                    rows_keep.append(row)
        except Exception as e:
            print(str(e))
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
