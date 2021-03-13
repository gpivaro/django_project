import mysql.connector
import json
import pandas as pd

""" Function to connect to the MySQL database and add one record to the database """

# Database variables:
database_name = "project_2"  # the name of the target database
table_name = "aircraft_data"

# import database_credentials as dbkeys
with open("/etc/config.json") as config_file:
    config = json.load(config_file)

# Create a function to connect to the MYSQL server
def database_connect(hostname, username, password, database=database_name):
    mydb = mysql.connector.connect(
        host=hostname,
        user=username,
        passwd=password,
        database=database
    )
    return mydb

# Return an object containing the MYSQL connection
mydb = database_connect(
    config.get("MYSQL_HOSTNAME"),
    config.get("MYSQL_USERNAME"),
    config.get("MYSQL_PASSWORD")
    )
print(mydb)

# Create the cursor to manipute databases
my_cursor = mydb.cursor()


# Retrieve data and convert the tuples to a list
my_cursor.execute(f"SELECT * FROM {database_name}.{table_name} ORDER BY id DESC LIMIT 5;")
list_records = []
for records in my_cursor:
    list_records.append(records)

# Convert tuples from database to dataframe
df = pd.DataFrame(list_records, columns = [
                                    "id",
                                    "icao24",
                                     "callsign",
                                     "origin_country",
                                     "time_position",
                                     "last_contact",
                                     "longitude",
                                     "latitude",
                                     "baro_altitude",
                                     "on_ground",
                                     "velocity",
                                     "true_track",
                                     "vertical_rate",
                                     "sensors",
                                     "geo_altitude",
                                     "squawk",
                                     "spi",
                                     "position_source"]
                 )

# Set the index to the primary key of the database
df.set_index('id',inplace=True)

# Convert the dataframe to dictionary
result_dict = df.to_dict(orient='records')

print(result_dict)