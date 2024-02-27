import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
from urllib.parse import urlparse, unquote
import time
import requests

downloads_path = str(Path.home() / "Downloads")
path_to_download = os.path.join(downloads_path, "apks")


def check_if_exist(driver, by, selector):
   try:
      driver.find_element(by, selector)
      return True
   except:
      return False


def get_bundle_ids():
   ids = []
   with open("output.csv", newline="", encoding="utf-8") as csvfile:
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
   options = webdriver.ChromeOptions()
   prefs = {"download.default_directory": path_to_download}
   options.add_experimental_option("prefs", prefs)
   driver = webdriver.Chrome(options)

   # time.sleep(5)
   # window_before = driver.window_handles[0]
   # driver.switch_to.window(window_before)

   try:
      driver.get(f"https://apkcombo.com/downloader/#package={bundle_id}")
      # generate_link_elem = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="apksumbit"]')))
      # generate_link_elem.click()
      list_architectures = WebDriverWait(driver, 20).until(
         EC.element_to_be_clickable((By.XPATH, '//*[@id="apkcombo-tab"]/div'))
      )
      li_list = list_architectures.find_elements(By.TAG_NAME, "ul")
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
      wget(href, f'{path_to_download}/{link[1]}_{filename.replace(':', '_')}')
    #  if(idx > 0):
    # #   print(f'{path_to_download}/{os.path.splitext(filename)[0]} ({idx}).apk')
    # #   WebDriverWait(driver, 60).until(file_exists(f'{path_to_download}/{os.path.splitext(filename)[0].replace(':', '_')} ({idx}).apk'))
    #  else:
    #   wget(href, f'{path_to_download}/{filename.replace(':', '_')}')
    # #   print(f'{path_to_download}/{filename}')
    # #   WebDriverWait(driver, 60).until(file_exists(f'{path_to_download}/{filename.replace(':', '_')}'))


isExist = os.path.exists(path_to_download)

if not isExist:
   os.makedirs(path_to_download)
bundle_ids = get_bundle_ids()

for id in bundle_ids:
   download_files(id)

# https://download.apkcombo.com/ua.ukrposhta.android.app/%D0%A3%D0%BA%D1%80%D0%BF%D0%BE%D1%88%D1%82%D0%B0_0.15.70_apkcombo.com.apk?ecp=dWEudWtycG9zaHRhLmFuZHJvaWQuYXBwLzAuMTUuNzAvMTYxLjI0ODk1YTNiYzUxZDVlYmI2NDdiYTllZjIzYTgxYzQyYmM2NDg5ZGYuYXBr&iat=1708971365&sig=a754292ca324adea6842a78211673c76&size=17032137&from=cf&version=latest&lang=en&fp=e782ac5fafc9086043cd0a079e0dcb8f&ip=45.12.24.124
