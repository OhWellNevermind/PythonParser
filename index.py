import csv
import csv_operations as cp
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
from urllib.parse import urlparse, unquote
from fake_useragent import UserAgent
import requests

ua = UserAgent()
user_agent = ua.random

downloads_path = str(Path.home() / "Downloads")
current_dir = os.getcwd()
path_to_download = os.path.join(current_dir, "apks")


options = webdriver.ChromeOptions()
prefs = {"download.default_directory": path_to_download}
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_experimental_option("prefs", prefs)
options.add_argument("start-maximized")
options.add_argument(f"--user-agent={user_agent}")
driver = webdriver.Chrome(options)


def create_apk_folder(csv_filename):
    csv_apk_folder_path = os.path.join(path_to_download, csv_filename)
    is_folder_exist = os.path.exists(csv_apk_folder_path)
    if is_folder_exist:
        return csv_apk_folder_path
    else:
        os.mkdir(csv_apk_folder_path)
        return csv_apk_folder_path


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


def handle_no_downloads(csv_file, download_to, bundle_id):
    try:
        driver.get(f"https://apps.evozi.com/apk-downloader/?id={bundle_id}")
    except:
        print("Не зміг відкрити посилання")
        return
    try:
        generate_link_elem = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div[3]/div[1]/div/div/div[2]/button[1]")
            )
        )
        generate_link_elem.click()
    except:
        print("Не вийшло знайти елемент або натиснути на кнопку")
        return
    try:
        href = (
            WebDriverWait(driver, 10)
            .until(
                EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[3]/div[1]/div/div/div[2]/a")
                )
            )
            .get_attribute("href")
        )
    except:
        print("Не вийшло знайти елемент")

    try:
        file = urlparse(href)
        filename = unquote(os.path.basename(file.path))
    except:
        return
    try:
        wget(href, f'{download_to}/{filename.replace(":", "_")}')
    except:
        print("Не зміг завантажити файл по посиланню")
        return
    with open("downloaded.csv", "a", newline="", encoding="utf-8") as file:
        print("Записую файл")
        writer = csv.writer(file)
        try:
            writer.writerow([bundle_id, f'{filename.replace(":", "_")}'])
        except Exception as e:
            print(f"Помилка при записі файлу. ErrorString: {str(e)}")
        file.close()
    cp.delete_downloaded_bundle_id(csv_file, bundle_id)


def download_files(csv_file, download_to, bundle_id):
    try:
        driver.get(f"https://apkcombo.com/downloader/#package={bundle_id}")
    except:
        print("Не зміг відкрити посилання")
        return
    try:
        list_architectures = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="apkcombo-tab"]/div'))
        )
        li_list = list_architectures.find_elements(By.CSS_SELECTOR, ".tree>ul")
    except:
        print("Не зміг знайти DOM елемент з файлами")
        handle_no_downloads(csv_file, download_to, bundle_id)
        return

    links_list = get_apk_links_list(li_list)

    if len(links_list) == 0:
        print("Посилань на завантаження файлів не знайдено")
        handle_no_downloads(csv_file, download_to, bundle_id)
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
            handle_no_downloads(csv_file, download_to, bundle_id)
            return
        with open("downloaded.csv", "a", newline="", encoding="utf-8") as file:
            print("Записую файл")
            writer = csv.writer(file)
            try:
                writer.writerow([bundle_id, f'{link[1]}_{filename.replace(":", "_")}'])
            except Exception as e:
                print(f"Помилка при записі файлу. ErrorString: {str(e)}")
        file.close()
    cp.delete_downloaded_bundle_id(csv_file, bundle_id)


def main():
    is_downloaded_exist = os.path.exists(os.path.join(current_dir, "downloaded.csv"))
    if not is_downloaded_exist:
        with open("downloaded.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["bundle_id", "filename"])

    csv_files = cp.get_all_csv_files()
    for csv_file in csv_files:
        if not csv_file.__contains__(".git"):
            csv_filename = os.path.splitext(os.path.basename(csv_file))[0]
            if csv_filename.__contains__("paid"):
                continue
            else:
                apk_download_to_path = create_apk_folder(csv_filename)
                bundle_ids = cp.get_bundle_ids(csv_file)
                for id in bundle_ids:
                    download_files(csv_file, apk_download_to_path, id)


main()
