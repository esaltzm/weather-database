import re
import os
import time
import boto3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

def lambda_handler(event, context):
    try:
        s3 = boto3.client('s3')

        options = Options()
        options.binary_location = '/opt/headless-chromium'
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--single-process')
        options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome('/opt/chromedriver',chrome_options=options)
        driver.get('https://www.ncei.noaa.gov/has/HAS.FileAppRouter?datasetname=RAP130&subqueryby=STATION&applname=&outdest=FILE')
        input_element = driver.find_element(By.NAME, "emailadd")
        input_element.send_keys("elisaltzman@gmail.com", Keys.RETURN)
        print('added email')
        submit_button = driver.find_element(By.CSS_SELECTOR, ".HASButton:first-child")
        submit_button.click()
        print('submitted form')
        source = driver.page_source
        regex = re.compile(r'HAS\d+')
        match = regex.search(source)
        end_url = 'http://www1.ncdc.noaa.gov/pub/has/model/' + match[0]
        print(end_url)
        driver.get(end_url)
        counter = 0
        while counter < 30:
            try:
                driver.find_element(By.XPATH, "//h1[text()='Not Found']")
                print('resource not loaded yet')
                time.sleep(5)
                driver.refresh()
                counter += 1
            except:
                print('resource loaded, proceeding')
                break
        link = driver.find_element(By.CSS_SELECTOR, "a[href*='.g2.tar']")
        print('found .g2.tar a tag')
        file_url = link.get_attribute("href")
        counter = 0
        while counter < 30:
            try:
                os.system(f'curl -o /tmp/file.tar {file_url}')
                break
            except Exception as e:
                print(f'{e} - waiting 5 seconds before trying again.')
                time.sleep(5)
                counter += 1
        print('downloaded .g2.tar')
        s3.upload_file('/tmp/file.tar', 'noaaweatherdatadaily', 'file.tar')
        print('uploaded to s3')
        os.remove('/tmp/file.tar')
        print('unzipped and removed')
    except Exception as e:
        print(e)
    finally:
        driver.quit()

