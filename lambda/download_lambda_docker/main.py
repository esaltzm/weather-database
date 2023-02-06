import re
import os
import time
import boto3
import json
from tempfile import mkdtemp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# Downloads target GRB2 zip, retrying if it is not ready yet and has a smaller than expected size

def download(file_url, driver, s3):
    counter = 0
    print('file url: ', file_url)
    while counter < 30:
        try:
            os.system(f'curl -o /tmp/file.g2.tar {file_url}')
            file_size = os.path.getsize('/tmp/file.g2.tar')
            if file_size < 300:
                os.remove('/tmp/file.g2.tar')
                raise Exception('Downloaded file size does not match the expected size')
            break
        except Exception as e:
            print(f'{e} - waiting 5 seconds before trying again.')
            time.sleep(5)
            counter += 1
    print('downloaded .g2.tar')
    s3.upload_file('/tmp/file.g2.tar', 'noaaweatherdatadaily', 'file.g2.tar')
    print('uploaded to s3')
    os.remove('/tmp/file.g2.tar')
    print('unzipped and removed')
    driver.quit()


def handler(event, context):

    # Specifying headless Chrome driver options

    options = webdriver.ChromeOptions()
    options.binary_location = '/opt/chrome/chrome'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1280x1696')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-dev-tools')
    options.add_argument('--no-zygote')
    options.add_argument(f'--user-data-dir={mkdtemp()}')
    options.add_argument(f'--data-path={mkdtemp()}')
    options.add_argument(f'--disk-cache-dir={mkdtemp()}')
    options.add_argument('--remote-debugging-port=9222')
    driver = webdriver.Chrome("/opt/chromedriver", options=options)

    end_url = event.get('end_url', None)
    s3 = boto3.client('s3')
    
    # Check if end_url was passed as argument (was parsed earlier, but download failed)

    if(end_url):
        driver.get(end_url)
        try:
            link = driver.find_element(By.CSS_SELECTOR, "a[href*='.g2.tar']")
            print('found .g2.tar a tag')
            cloudwatch = boto3.client('events')
            secondary_download = event.get('secondary_download_rule', None)

            # If GRB2 zip download link is accessible, remove hourly cloudwatch invocation and proceed to download

            if secondary_download:
                cloudwatch.delete_rule(Name='secondary_download_rule')
                print('deleted secondary download rule')
            file_url = link.get_attribute('href')
            download(file_url, driver, s3)
            return 'Downloaded latest data to s3 bucket'
        except Exception as e:

            # If 

            return f'Exception: {e}\nTrying again in 1 hour'
    
    # if no end_url, this is the first function call and end_url must be retrieved with Chrome driver

    else:

        # Process forms at NOAA data store to request download link for latest day of weather data

        driver.get('https://www.ncei.noaa.gov/has/HAS.FileAppRouter?datasetname=RAP130&subqueryby=STATION&applname=&outdest=FILE')
        input_element = driver.find_element(By.NAME, 'emailadd')
        input_element.send_keys('elisaltzman@gmail.com', Keys.RETURN)
        print('added email')
        submit_button = driver.find_element(By.CSS_SELECTOR, '.HASButton:first-child')
        submit_button.click()
        print('submitted form')
        source = driver.page_source
        regex = re.compile(r'HAS\d+')
        match = regex.search(source)

        # Extract end url (where download link will be available after processing)

        end_url = 'http://www1.ncdc.noaa.gov/pub/has/model/' + match[0]
        print(end_url)
        driver.get(end_url)
        counter = 0

        # Try accessing end url 30 times, with 5 second delay in between

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

        # Try accessing GRB2 download link

        try:
            link = driver.find_element(By.CSS_SELECTOR, "a[href*='.g2.tar']")
            print('found .g2.tar a tag')
        except:

            # If it is not found on the page, download processing is taking too long. Call function hourly until success

            print('Resource taking longer than usual to retrieve, activating secondary download')
            cloudwatch = boto3.client('events')
            cloudwatch.put_rule(
                Name='secondary_download_rule',
                ScheduleExpression='rate(1 hour)',
                State='ENABLED'
            )
            cloudwatch.put_targets(
                Rule='secondary_download_rule',
                Targets=[
                    {
                        'Id': 'LambdaTarget',
                        'Arn': 'arn:aws:lambda:us-east-1:813509553407:function:download-lambda-docker-prod-download',
                        'Input': json.dumps({
                            'end_url': end_url
                        })
                    }
                ]
            )
            return 'Calling download function again in 1 hour'
        file_url = link.get_attribute('href')
        counter = 0
        print('file url: ', file_url)
        time.sleep(5)
        download(file_url, driver, s3)
        return 'downloaded latest data to s3 bucket'
