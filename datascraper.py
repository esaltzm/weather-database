import mechanicalsoup

browser = mechanicalsoup.StatefulBrowser()
file_selection = browser.open("https://www.ncei.noaa.gov/has/HAS.FileAppRouter?datasetname=RAP130&subqueryby=STATION&applname=&outdest=FILE")

print(file_selection.soup)