import mysql.connector as database
from dotenv import dotenv_values

config = dotenv_values('.env')
connection = database.connect(user=config['USERNAME'], password=config['PASSWORD'], host=config['HOST'], database='weather_db')
cursor = connection.cursor()
cursor.execute('select count(*) from automation;')
result = cursor.fetchone()[0]
print('predelete: ', result)
cursor.execute('select count(*) from automation where time_start <= 1674745200;')
result = cursor.fetchone()[0]
print('will delete: ', result)
cursor.execute('SELECT UNIQUE time_start FROM automation WHERE time_start <= 1674745200 ORDER BY time_start DESC;')
result = cursor.fetchall()
print('after delete: ', result)

