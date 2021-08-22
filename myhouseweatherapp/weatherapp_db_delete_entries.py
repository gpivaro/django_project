import mysql.connector
import os
import json
import datetime as dt


target_log_filepath = f"{os.path.expanduser('~')}/db_records_log.txt"

# Create a string with the time delta of x days
target_date = dt.datetime.date(dt.datetime.now() - dt.timedelta(days=120))
print(f"""The target date is {target_date.strftime("%Y-%m-%d")}.\n""")


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
        FROM djangowebsite.myhouseweatherapp_weather 
        where meas_time < '{target_date.strftime("%Y-%m-%d")}'
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
        FROM djangowebsite.myhouseweatherapp_weather 
        WHERE meas_time < '{target_date.strftime("%Y-%m-%d")}';
        """
)


# commit changes
mydb.commit()


# Select values that match the criteria
my_cursor.execute(
    f"""SELECT count(*) 
        FROM djangowebsite.myhouseweatherapp_weather 
        where meas_time < '{target_date.strftime("%Y-%m-%d")}' 
        order by meas_time desc 
        limit 1;
        """
)

for x in my_cursor:
    print(
        f"""There are {x[0]} records that are older than {target_date.strftime("%Y-%m-%d")}."""
    )

