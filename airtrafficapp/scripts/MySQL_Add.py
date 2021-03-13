import mysql.connector
import json

# Function to connect to the MySQL database and add one record to the database """

# Database variables:
database_name = "djangowebsite"  # the name of the target database
table_name = "airtrafficapp_aircrafts"

# import database_credentials as dbkeys
with open("/etc/config.json") as config_file:
    config = json.load(config_file)

# Create a function to connect to the MYSQL server
def database_connect(hostname, username, password, database=database_name):
    mydb = mysql.connector.connect(
        host=hostname, user=username, passwd=password, database=database
    )
    return mydb


# Return an object containing the MYSQL connection
mydb = database_connect(
    config.get("MYSQL_HOSTNAME"),
    config.get("MYSQL_USERNAME"),
    config.get("MYSQL_PASSWORD"),
)
print(mydb)

# Create the cursor to manipute databases
my_cursor = mydb.cursor()

my_cursor.execute(
    f"SELECT * FROM {database_name}.{table_name} ORDER BY id DESC LIMIT 1;"
)
for records in my_cursor:
    print(records)
    print(records[0])


# Create place holders records to insert into the table
sqlStuff = f"""INSERT INTO {table_name} (icao24, 
                                        callsign,
                                        origin_country,
                                        time_position,
                                        last_contact,
                                        longitude,
                                        latitude,
                                        baro_altitude,
                                        on_ground,
                                        velocity,
                                        true_track,
                                        vertical_rate,
                                        sensors,
                                        geo_altitude,
                                        squawk,
                                        spi,
                                        position_source,
                                        time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """


# Save the record to the database
# single element at the time
def add_to_database(data):
    try:
        # Add records to the database
        my_cursor.execute(sqlStuff, data)

        # Commit changes to the database
        mydb.commit()

        # print('Record Added to DB')
    except:
        print("Error Saving to DB")

    mydb.close()


# Save the record to the database with
# multiple records at the same time
def add_many_database(data):
    try:
        # Add records to the database
        my_cursor.executemany(sqlStuff, data)

        # Commit changes to the database
        mydb.commit()

        print("Record Added to DB")
    except:
        print("Error Saving to DB")

    mydb.close()
