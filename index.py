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
path_to_download = os.path.join(downloads_path, "apks")
csv_file = "output.csv"

options = webdriver.ChromeOptions()
prefs = {"download.default_directory": path_to_download}
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options)


def delete_downloaded_bundle_id():
    with open(csv_file, encoding="utf-8") as rf, open(
        "myfile.csv.temp", "w", encoding="utf-8"
    ) as wf:
        for i, line in enumerate(rf):
            if i != 1:
                wf.write(line)
    os.replace("myfile.csv.temp", csv_file)


def check_if_exist(by, selector):
    try:
        driver.find_element(by, selector)
        return True
    except:
        return False


def get_bundle_ids():
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
    except:
        return li_arr
    finally:
        return li_arr


def file_exists(path):
    def _predicate(_):
        return Path(path).is_file()

    return _predicate


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


def download_files(bundle_id):
    try:
        driver.get(f"https://apkcombo.com/downloader/#package={bundle_id}")
        list_architectures = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="apkcombo-tab"]/div'))
        )
        li_list = list_architectures.find_elements(By.CSS_SELECTOR, ".tree>ul")
    except:
        return

    links_list = get_apk_links_list(li_list)

    if len(links_list) == 0:
        return

    for link in links_list:
        href = link[0]
        file = urlparse(href)
        filename = os.path.basename(file.path)
        filename = unquote(filename)
        print("Намагаюсь отримати файл")
        wget(href, f'{path_to_download}/{link[1]}_{filename.replace(":", "_")}')
        with open("downloaded.csv", "a", newline="", encoding="utf-8") as file:
            print("Записую файл")
            writer = csv.writer(file)
            writer.writerow([bundle_id, f'{link[1]}_{filename.replace(":", "_")}'])
        file.close()


def main():
    is_folder_exist = os.path.exists(path_to_download)
    with open("downloaded.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["bundle_id", "filename"])

    if not is_folder_exist:
        os.makedirs(path_to_download)

    bundle_ids = get_bundle_ids()

    for id in bundle_ids:
        download_files(id)
        delete_downloaded_bundle_id()


main()
