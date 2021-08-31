import mysql.connector
import os
import json
import datetime as dt

database_name = "djangowebsite"  # the name of the target database
table_name = "airtrafficapp_aircrafts"

target_log_filepath = (
    f"{os.path.expanduser('~')}/mylogs/airtrafficapp_db_records_log.txt"
)

# Create a string with the time delta of x days
target_date = dt.datetime.date(dt.datetime.now() - dt.timedelta(days=60))
print(f"""The target date is {target_date.strftime("%Y-%m-%d")}.\n""")
target_date_unix = int(target_date.strftime("%s"))

with open("/etc/config.json") as config_file:
    config = json.load(config_file)


# Create a function to connect to the MYSQL server
def database_connect(hostname, port, username, password, database=""):
    mydb = mysql.connector.connect(
        host=hostname, port=port, user=username, passwd=password, database=database
    )
    return mydb


# Return an object containing the MYSQL connection
mydb = database_connect(
    config.get("MYSQL_HOSTNAME"),
    config.get("MYSQL_PORT"),
    config.get("MYSQL_USERNAME"),
    config.get("MYSQL_PASSWORD"),
    database="djangowebsite",
)
print(f"""Message from database: {mydb}\n""")


# Create the cursor to manipute databases
my_cursor = mydb.cursor()


# Select values that match the criteria
my_cursor.execute(
    f"""SELECT count(*) 
        FROM {database_name}.{table_name} 
        where time < '{target_date_unix}'
        """
)

for x in my_cursor:
    print(
        f"""There are {x[0]} records that are older than {target_date.strftime("%Y-%m-%d")} at ({dt.datetime.now()}).\n"""
    )

with open(target_log_filepath, "a") as f:
    f.write(
        f"""There are {x[0]} records that are older than {target_date.strftime("%Y-%m-%d")} (at {dt.datetime.now()}).\n"""
    )

# Delete values that match the criteria
my_cursor.execute(
    f"""DELETE 
        FROM {database_name}.{table_name}
        WHERE time < '{target_date_unix}';
        """
)


# commit changes
mydb.commit()


# Select values that match the criteria
my_cursor.execute(
    f"""SELECT count(*) 
        FROM {database_name}.{table_name} 
        where time < '{target_date_unix}' 
        order by time desc 
        limit 1;
        """
)

for x in my_cursor:
    print(
        f"""There are {x[0]} records that are older than {target_date.strftime("%Y-%m-%d")}."""
    )

