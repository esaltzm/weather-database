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


def handler(event, context):

    s3 = boto3.client('s3')

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
    
    if(end_url):
        driver.get(end_url)
        try:
            link = driver.find_element(By.CSS_SELECTOR, "a[href*='.g2.tar']")
            print('found .g2.tar a tag')
            cloudwatch = boto3.client('events')
            secondary_download = event.get('secondary_download_rule', None)
            if secondary_download:
                cloudwatch.delete_rule(Name='secondary_download_rule')
                print('deleted secondary download rule')
            file_url = link.get_attribute('href')
            counter = 0
            print('file url: ', file_url)
            time.sleep(5)
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
            return 'Downloaded latest data to s3 bucket'
        except Exception as e:
            return f'Exception: {e}\nTrying again in 1 hour'
    else:
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
        try:
            link = driver.find_element(By.CSS_SELECTOR, "a[href*='.g2.tar']")
            print('found .g2.tar a tag')
        except:
            print('Resource taking longer than usual to retrieve, activating secondary download')
            cloudwatch = boto3.client('events')
            try:
                cloudwatch.describe_rule(Name='secondary_download_rule')
            except cloudwatch.exceptions.ResourceNotFoundException:
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
            return 'Resource taking longer than usual to retrieve'
        file_url = link.get_attribute('href')
        counter = 0
        print('file url: ', file_url)
        time.sleep(5)
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
        return 'downloaded latest data to s3 bucket'
