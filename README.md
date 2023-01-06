# Weather Database

This project was inspired by not wanting to pay to use someone else's historical weather API. After running out of a free trial for the weather.com, I got to thinking - the many paid weather APIs out there are not all funding weather stations or satellites and collecting their own data, right!? I assume they take their data from a public source such as the NOAA and then sell this data processed into an easily accessible API, so I attempted to do the same thing on my own.
<br/>To begin with, I used a shell script to downloaded a year's worth of data from the [NOAA RAP weather model](https://www.ncei.noaa.gov/products/weather-climate-models/rapid-refresh-update), which offers weather data at a resolution of 1 hour and every 12km over the coverage area - it was around 250GB of raw data. This weather data is stored in the GRIB2 file format, which I parsed using the Python modules xarray (with the cfgrib engine) and pandas. After loading the parameters I was interested in to a pandas dataframe, I was able to pass each datapoint as a row in a MariaDB SQL table. This table is hosted by Amazon Web Services RDS service - adding a year's data was over 130 million individual rows, and took nearly two days. Overall, this project taught me a lot about database administration and its challenges. 

Here is the first image I received after processing the data (using matplotlib), showing a map of temperature over the coverage area:
<img src="https://i.imgur.com/j5y0S6L.png" alt="heatmap contour plot of temperature, showing a rough outline of north america" width="500"/>

## Technologies Used

- Python
- [xarray](https://docs.xarray.dev/en/stable/)
- [pandas](https://pandas.pydata.org/about/index.html)
- [matplotlib](https://matplotlib.org/)
- [shapely](https://shapely.readthedocs.io/en/stable/manual.html)
- [MariaDB](https://mariadb.org/about/) - chose this over MySQL because it's open source
- [Amazon Web Services RDS](https://aws.amazon.com/rds/features/)
- [Selenium](https://www.selenium.dev/documentation/) - future feature

## Features
- Indices - one on time, another composite index on latitude and longitude (sped sample query from 13s to 300ms)!

## Code Snippets

- Bulk downloading a year's worth of data using shell script:

        total=$(wc -l < "files.txt")
        counter=1
        for file in `cat files.txt`; do
            echo downloading $file "(...$counter / $total...)";
            curl https://www.ncei.noaa.gov/pub/has/model/HAS012341222/$file > /Volumes/Untitled/$file;
            counter = $((counter+1))
        done
        
- Main function of GRIB2 file parser (only parses every 3rd hour):

        for folder in sorted(os.listdir(path)):
            if os.path.isdir(os.path.join(path, folder)):
                print(f'Parsing folder: {folder}')
                for filename in sorted(os.listdir('/Volumes/Untitled/grb2_files/' + folder)):
                    hour = filename.split('.')[0][-2:]
                    if int(hour) % 3 == 0: # add every 3rd hour to db
                        rows = extract_data(path, folder, filename)
                        write_to_db(rows, cursor)

## Problems and Solutions

### Bulk Data Download
I initially tried to download each file manually in the browser, but that took way too much time. My next step was to attempt to use some Chrome download manager extensions, but these too were poorly designed and confusing to use. In the end, I realized I could make my own 'download manager' so I learned a bit of shell script (see above) to efficiently automate this task.

### Database Size
I knew from the start that my goal of loading a year of data to the database would make space a challenge, especially on the AWS free tier. One step I took after realizing I might go over this size was to switch from my initial PostgreSQL database to a MariaDB database. While Postgres offers more features and is a more modern database, for size MariaDB was really helpful. One day's worth of data went from ~90mb to around ~50mb!

### Creating Indices and running out of space
With a database this size, I knew I would need some indices to improve query runtime. I chose to add indexes after the table was created, but one issue I ran into with this was that the CREATE INDEX process copies the entire table before executing, which meant I would go over my alotted 20gb on the AWS free tier. Here is a plot of the memory capacity of my database while I was trying to add indices (y-axis is remaining space in mb):
![plot of remaining db space over time](https://i.imgur.com/WyM4aJE.png)
After multiple CREATE INDEX attempts failed due to running out of memory, I realized I would have to cut my database size to keep the combined memory of db, the db copy, and the indices under 20gb. To cut the size, I dropped the column 'crain' which was a boolean saying whether it was raining or not. This freed just 0.3gb, so I made some more changes: alter all weather attribute columns from a real (8 bytes) to a float (4 bytes) - this dropped a whole 2gb! I then added a triple composite index on time, latitude, and longitude, which dropped a sample query runtime from ~13s to ~300ms. 

## Future Improvements
- Currently, the database only has datapoints that lie within the continental U.S. (on land), which results in some distortion in the plots I used to visualize this data on the [frontend](https://github.com/esaltzm/skyscan-frontend/). I want to go back and add data for the surrounding oceans and Great Lakes so that when this frontend view is zoomed out, it has complete data to pass to the plot. 
![plot of precip rate showing distortion out of bounds of conus](https://i.imgur.com/54JiYaG.png)
- I would love for this database to stay current, adding each day's new data to the database and removing the oldest day's data in a Last In First Out cache. This would involve automating the download and parsing process - part of which is done, but the interactions with the NOAA data request web form would have to be automated using Selenium. I attempted this, but did not have the time to implement within the project week.

