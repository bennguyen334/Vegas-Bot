#import libraries
import sqlite3

#connect to database
connection = sqlite3.connect('database.db')
print ("Opened database successfully")

#create Users Table in database
connection.execute('CREATE TABLE Users(usernameID TEXT, Balance INTEGER)')
print ("Users Table Added")

connection.close()
