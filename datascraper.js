const express = require('express')
const { Builder, By, Key } = require('selenium-webdriver')
const fs = require('fs')
const request = require('request')

const app = express()
const port = 3000

app.get('/', async (req, res) => {
    try {
        const data = await getFileNames()
        res.status(200).json(data)
    } catch (error) {
        res.status(500).json({
            message: 'Server error occurred',
        })
    }
})

app.listen(port, () => {
    console.log(`Example app listening at http://localhost:${port}`)
})

const getFileNames = async () => {
    try {
        driver = await new Builder().forBrowser('chrome').build()
        await driver.get('https://www.ncei.noaa.gov/has/HAS.FileAppRouter?datasetname=RAP130&subqueryby=STATION&applname=&outdest=FILE')
        let inputElement = await driver.findElement(By.name("emailadd"))
        await inputElement.sendKeys("elisaltzman@gmail.com", Key.RETURN)
        let submitButton = await driver.findElement(By.css(".HASButton:first-child"))
        await submitButton.click()
        await driver.sleep(5000)
        const source = await driver.getPageSource()
        const regex = new RegExp('HAS\\d+')
        const match = source.match(regex)
        let endUrl = 'http://www1.ncdc.noaa.gov/pub/has/model/' + match[0] + `/rap_130_${date}00.g2.tar`
        return endUrl
    } catch (error) {
        throw new Error(error)
    } finally {
        await driver.quit()
    }
}