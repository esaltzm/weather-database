# Weather Database

This project was inspired by not wanting to pay to use someone else's historical weather API. After running out of a free trial for the weather.com, I got to thinking - the many paid weather APIs out there are not all funding weather stations or satellites and collecting their own data, right!? I assume they take their data from a public source such as the NOAA and then sell this data processed into an easily accessible API, so I attempted to do the same thing on my own.
<br/><br/>To begin with, I used a shell script to downloaded a year's worth of data from the [NOAA RAP weather model](https://www.ncei.noaa.gov/products/weather-climate-models/rapid-refresh-update), which offers weather data at a resolution of 1 hour and every 12km over the coverage area - it was around 250GB of raw data. This weather data is stored in the GRIB2 file format, which I parsed using the Python modules XArray (with the cfgrib engine) and Pandas. After loading the parameters I was interested in to a Pandas dataframe, I was able to pass each datapoint as a row in a MariaDB SQL table. This table is hosted by Amazon Web Services RDS service - adding a year's data was nearly 300 million individual rows, and took nearly two days. Overall, this project taught me a lot about database administration and its challenges. 
<br/><br/>Lastly, I knew I wanted this database to be automatically updated, not just store a year's worth of data from the time it was initially created. I envisioned a first-in first-out cache system, where every day the most recent data would be added automatically, and the oldest day of data would be removed (ideally, all data would stay and the DB would only grow, but storage limits dictate that it can only hold one year at a time). To accomplish this, I utilized two serverless AWS Lambda functions - one is a downloader that uses Selenium to scrape the latest data from the NOAA's web form and save it to a S3 storage bucket. The next function is a parser, which uses a modified version of my local parser to parse the file in the S3 bucket, post it to the database, and then empty the bucket after parsing. These functions are scheduled to execute daily using AWS CloudWatch events. 

Here is the first image I received after processing the data (using matplotlib), showing a map of temperature over the coverage area:

<img src="https://i.imgur.com/j5y0S6L.png" alt="heatmap contour plot of temperature, showing a rough outline of north america" width="500"/>

## Technologies Used

- [AWS RDS](https://aws.amazon.com/rds/features/)
- [AWS Lambda](https://aws.amazon.com/lambda/features/)
- [AWS S3](https://aws.amazon.com/s3/features/)
- [AWS CloudWatch](https://aws.amazon.com/cloudwatch/features/)
- [Selenium](https://www.selenium.dev/documentation/)
- [Docker](https://docs.docker.com/get-started/)
- [MariaDB](https://mariadb.org/about/)
- [xarray](https://docs.xarray.dev/en/stable/)
- [pandas](https://pandas.pydata.org/about/index.html)
- [matplotlib](https://matplotlib.org/)
- [shapely](https://shapely.readthedocs.io/en/stable/manual.html)

## Database Features
- I used MyISAM over the InnoDB engine because even though it is older and less performant on queries, it uses less disk space than InnoDB
![updated database info](https://i.imgur.com/s9TtLuo.png)

- Here is how the data is laid out in the table
![sql query showing first row of table](https://i.imgur.com/WRUglTB.png)

- Data types for each column in the table (designed to reduce data storage where possible)
![sql query for column data types](https://i.imgur.com/b8CEWA6.png)

## Code Snippets

- First step for scraping latest data from NOAA data portal:

            driver.get('https://www.ncei.noaa.gov/has/HAS.FileAppRouter?datasetname=RAP130&subqueryby=STATION&applname=&outdest=FILE')
            input_element = driver.find_element(By.NAME, "emailadd")
            input_element.send_keys("elisaltzman@gmail.com", Keys.RETURN)
            submit_button = driver.find_element(By.CSS_SELECTOR, ".HASButton:first-child")
            submit_button.click()
            source = driver.page_source
            regex = re.compile(r'HAS\d+')
            match = regex.search(source)
            end_url = 'http://www1.ncdc.noaa.gov/pub/has/model/' + match[0]
        
- Inserting data into the SQL table:

        query = """INSERT INTO weather (time_start, latitude, longitude, t, gust, sde, prate, ltng) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
        for row in rows[8000:130000]: # this range contains bounding box coords
        time_start, time_stop, latitude, longitude, t, gust, sde, prate, crain, ltng = row
        if latitude >= 22.262387 and latitude <= 50.648574 and longitude >= -127.640625 and longitude <= -64.359375:
            records.append((time_start, latitude, longitude, t, gust, sde, prate, ltng))
        cursor.executemany(query, records)

## Problems and Solutions

### Bulk Data Download
I initially tried to download each file manually in the browser, but that took way too much time. My next step was to attempt to use some Chrome download manager extensions, but these too were poorly designed and confusing to use. In the end, I realized I could make my own 'download manager' so I learned a bit of shell script to efficiently automate this task.

### Database Size
I knew from the start that my goal of loading a year of data to the database would make space a challenge, especially on the AWS free tier. One step I took after realizing I might go over this size was to switch from my initial PostgreSQL database to a MariaDB database. While Postgres offers more features and is a more modern database, for size MariaDB was really helpful. The same data took about 60% of the storage size using this database.

### Creating indices and running out of space
With a database this size, I knew I would need some indices to improve query runtime. I chose to add indexes after the table was created, but one issue I ran into with this was that the CREATE INDEX process copies the entire table before executing, which meant I would go over my alotted 20gb on the AWS free tier. Here is a plot of the memory capacity of my database while I was trying to add indices (y-axis is remaining space in mb):
![plot of remaining db space over time](https://i.imgur.com/WyM4aJE.png)
After multiple CREATE INDEX attempts failed due to running out of memory, I realized I would have to cut my database size to keep the combined memory of db, the db copy, and the indices under 20gb. To cut the size, I dropped the column 'crain' which was a boolean saying whether it was raining or not. This freed just 0.3gb, so I made some more changes: alter all weather attribute columns from a real (8 bytes) to a float (4 bytes) - this dropped a whole 2gb! I then added a triple composite index on time, latitude, and longitude, which dropped a sample query runtime from ~13s to ~300ms.

### AWS Lambda functions running out of layer storage
AWS Lambda functions utilize "layers" for any necessary imports not included in Python, and limits the size of these layers to just 250MB. Because I was using some pretty heavy imports (Chrome driver, cfgrib, pandas) I ran over this limit. The workaround I found is that if you use a Docker container to run your functions within, you have 10GB of space allocated for each container, which was more than enough for me. It was tough to get the Dockerfile right for the parser function, as it required some built C libraries, but I eventually got working containers for both my functions to run serverless in the cloud. 

## Future Improvements
- My latest idea for this project is another Lambda function that will run daily, executing SQL queries for different weather records/extremes from the database (i.e. hottest average day, highest snow depth, etc), and saving those results to a secondary MySQL table. On the frontend, users will be able to select a record they want to view, and it will direct them to the right time/place to view that data without running a heavy SQL query every time a user wants that information. Here are a few examples of records I found interesting (as of 2/1/2023):

- Hottest average day in U.S. in the last year - July 20, 2022 (83F average)
![sql query for hottest day](https://i.imgur.com/BFPAsEP.png)
![map showing high temps](https://i.imgur.com/haabaTg.png)

- Highest individual temperature in the U.S. in the last year - July 17, 2022 (122F in Death Valley, CA) <em>This was not the real record, which was 127F on September 1, 2022, also in Death Valley (I suspect by only capturing every 3rd hour for the database, I missed this point)</em>
![sql query for highest temp](https://i.imgur.com/EJQLJhZ.png)
![map showing death valley](https://i.imgur.com/fYrOVt4.png)

- Coldest average day - December 24, 2022 (31F average)
![sql query for lowest average temp](https://i.imgur.com/ZdLQRMu.png)
![map showing death valley](https://i.imgur.com/Q3lgpS0.png)

- Lowest individual temperature - February 13, 2022 (-45F in Lake Nipigon, Ontario, Canada)
![map showing lake w cold temp](https://i.imgur.com/yEBkNKH.png)

- Highest individual snow level - April 19, 2022 (25ft in Lillooet Icefield, British Columbia, Canada)
![sql query for highest sde](https://i.imgur.com/BUjYBYz.png)
![map of ice field](https://i.imgur.com/Oc7z11C.png)

- Windiest day - September 28, 2022 (Hurricane Ian approaches Florida)
![hurricane approaching fl](https://i.imgur.com/pnykW3I.png)

