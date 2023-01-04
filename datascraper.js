const {Builder} = require('selenium-webdriver')
const chrome = require('selenium-webdriver/chrome')

let driver = new Builder()
    .forBrowser('chrome')
    .setChromeOptions(new chrome.Options().headless())
    .build()

driver.get('https://www.ncei.noaa.gov/has/HAS.FileAppRouter?datasetname=RAP130&subqueryby=STATION&applname=&outdest=FILE')

driver.quit()
