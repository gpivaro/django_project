import mysql.connector
import json

#Function to connect to the MySQL database and delete rows older than 7 days """

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


my_cursor.execute(f"DELETE FROM {database_name}.{table_name} WHERE FROM_UNIXTIME(time, '%Y-%m-%d') < NOW() - INTERVAL 7 DAY;")

my_cursor.execute(f"SELECT * FROM {database_name}.{table_name} ORDER BY id LIMIT 1;")
for records in my_cursor:
    print(records)
    print(records[0])

my_cursor.execute(f"SELECT * FROM {database_name}.{table_name} ORDER BY id DESC LIMIT 1;")
for records in my_cursor:
    print(records)
    print(records[0])