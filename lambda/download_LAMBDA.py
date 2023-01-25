import re
import time
import os
import tarfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

try:
    driver = webdriver.Chrome()
    driver.get('https://www.ncei.noaa.gov/has/HAS.FileAppRouter?datasetname=RAP130&subqueryby=STATION&applname=&outdest=FILE')
    input_element = driver.find_element(By.NAME, "emailadd")
    input_element.send_keys("elisaltzman@gmail.com", Keys.RETURN)
    print('added email')
    submit_button = driver.find_element(By.CSS_SELECTOR, ".HASButton:first-child")
    submit_button.click()
    print('submitted form')
    time.sleep(5)
    source = driver.page_source
    regex = re.compile(r'HAS\d+')
    match = regex.search(source)
    end_url = 'http://www1.ncdc.noaa.gov/pub/has/model/' + match[0]
    print(end_url)
    time.sleep(10)
    driver.get(end_url)
    while True:
        try:
            not_found = driver.find_element(By.XPATH, "//h1[text()='Not Found']")
            print('resource not loaded yet')
            time.sleep(10)
            driver.refresh()
        except:
            print('resource loaded, proceeding')
            break
    link = driver.find_element(By.CSS_SELECTOR, "a[href*='.g2.tar']")
    print('found .g2.tar a tag')
    file_url = link.get_attribute("href")
    file_name = file_url.split("/")[-1]
    os.system(f"wget {file_url}")
    print('downloaded .g2.tar')
    with tarfile.open(file_name, "r:") as tar:
        tar.extractall()
    print('unzipped')
    os.mkdir("grb2_files")
    os.system(f"mv *.g2 grb2_files/")
    print('moved to grb2_files')
except Exception as e:
    print(e)
finally:
    driver.quit()

