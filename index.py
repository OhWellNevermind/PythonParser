import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
from urllib.parse import urlparse, unquote
import requests


downloads_path = str(Path.home() / "Downloads")
current_dir = os.getcwd()
path_to_download = os.path.join(current_dir, "apks")
csv_files_path = os.path.abspath("./csv")

options = webdriver.ChromeOptions()
prefs = {"download.default_directory": path_to_download}
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options)


def get_all_csv_files():
    for dirpath, _, filenames in os.walk(csv_files_path):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


def create_apk_folder(csv_filename):
    csv_apk_folder_path = os.path.join(path_to_download, csv_filename)
    is_folder_exist = os.path.exists(csv_apk_folder_path)
    if is_folder_exist:
        return csv_apk_folder_path
    else:
        os.mkdir(csv_apk_folder_path)
        return csv_apk_folder_path


def delete_downloaded_bundle_id(csv_file, bundle_id):
    rows_keep = []
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        print(bundle_id)
        rows_keep = [row for row in reader if not row[5].__contains__(bundle_id)]

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


def get_apk_links_list(list):
    li_arr = []
    try:
        for link in list:
            extension = link.find_element(By.CLASS_NAME, "type-apk").text
            arch = link.find_element(By.CLASS_NAME, "blur").text
            href = link.find_element(By.TAG_NAME, "a").get_attribute("href")
            if extension == "APK":
                li_arr.append([href, arch])
    except Exception as e:
        print(f"Щось сталося під час парсингу посилань на файли: ErrorString: {str(e)}")
        return li_arr
    finally:
        return li_arr


def wget(url, output_file):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(output_file, "wb") as f:
                f.write(response.content)
            print(f"Завантажено з {url} і збережено у {output_file}")
        else:
            print(f"Помилка: отримано код статусу {response.status_code}")
    except Exception as e:
        print(f"Помилка під час завантаження: {str(e)}")


def download_files(csv_file, download_to, bundle_id):
    try:
        driver.get(f"https://apkcombo.com/downloader/#package={bundle_id}")
    except:
        print("Не зміг відкрити посилання")
    try:
        list_architectures = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="apkcombo-tab"]/div'))
        )
        li_list = list_architectures.find_elements(By.CSS_SELECTOR, ".tree>ul")
    except:
        print("Не зміг знайти DOM елемент з файлами")
        return

    links_list = get_apk_links_list(li_list)

    if len(links_list) == 0:
        print("Посилань на завантаження файлів не знайдено")
        return

    for link in links_list:
        href = link[0]
        file = urlparse(href)
        filename = os.path.basename(file.path)
        filename = unquote(filename)
        print("Намагаюсь отримати файл")
        try:
            wget(href, f'{download_to}/{link[1]}_{filename.replace(":", "_")}')
        except:
            print("Не зміг завантажити файл по посиланню")
            return
        with open("downloaded.csv", "a", newline="", encoding="utf-8") as file:
            print("Записую файл")
            writer = csv.writer(file)
            try:
                writer.writerow([bundle_id, f'{link[1]}_{filename.replace(":", "_")}'])
            except Exception as e:
                print(f"Помилка при записі файлу. ErrorString: {str(e)}")
        file.close()
    delete_downloaded_bundle_id(csv_file, bundle_id)


def main():
    is_downloaded_exist = os.path.exists(os.path.join(current_dir, "downloaded.csv"))
    if not is_downloaded_exist:
        with open("downloaded.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["bundle_id", "filename"])

    csv_files = get_all_csv_files()
    for csv_file in csv_files:
        if not csv_file.__contains__(".git"):
            csv_filename = os.path.splitext(os.path.basename(csv_file))[0]
            if csv_filename.__contains__("paid"):
                continue
            else:
                apk_download_to_path = create_apk_folder(csv_filename)
                bundle_ids = get_bundle_ids(csv_file)
                for id in bundle_ids:
                    download_files(csv_file, apk_download_to_path, id)


main()
