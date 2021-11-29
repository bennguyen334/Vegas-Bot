import sqlite3

conn = sqlite3.connect('VegasBot.db')

sql_create_users_table = """ CREATE TABLE IF NOT EXISTS Users (
                                        userID VARCHAR(21) NOT NULL,
                                        balance INT NOT NULL,
                                        lastcollected datetime
                                    ); """


conn.execute(sql_create_users_table)
conn.commit()
conn.close()