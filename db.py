import sqlite3 as sql
import datetime
class Db:
    def add_user(self, val, user_id):
        with sql.connect("VegasBot.db") as con:
            cur = con.cursor()
            cur.execute(''' INSERT INTO Users (balance, userID) VALUES (?,?);''', (val, user_id))
            con.commit()

    def add(self, val, id):
        tf = True
        with sql.connect("VegasBot.db") as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM Users WHERE userID = ?;", (id,))
            num = float(cur.fetchone()[0])
            if num == 0:
                if val < 0:
                    val = 0
                self.add_user(val, id)
            else:
                cur.execute("SELECT balance FROM Users WHERE userID=?;", (id,))
                balance = float(cur.fetchone()[0])
                if balance + val < 0:
                    tf = False
                else:
                    cur.execute('''UPDATE Users SET balance=? WHERE userID = ?;''', (balance+val, id))
            con.commit()
        return tf

    def can_user_collect(self, id):
        conn = sql.connect("VegasBot.db")
        cur = conn.cursor()
        cur.execute("SELECT lastcollected FROM Users WHERE userID=?;", (id,))
        if(cur.fetchone() is None):
            return True
        else:
            cur.execute("SELECT lastcollected FROM Users WHERE userID=?;", (id,))
            lastCollected = datetime.datetime.strptime(cur.fetchone()[0], "%Y-%m-%dT%H:%M:%S.%f")
            if(datetime.datetime.date(lastCollected) == datetime.datetime.date(datetime.datetime.today())):
                conn.close()
                return False
            else:
                conn.close()
                return True
    
    def setLastCollected(self, id):
        conn = sql.connect("VegasBot.db")
        cur = conn.cursor()
        cur.execute(''' UPDATE Users SET lastcollected=? WHERE userID=? ''', (str(datetime.datetime.now().isoformat()), str(id)))
        conn.commit()
        conn.close()
    
    def get_balance(self, id):
        with sql.connect("VegasBot.db") as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM Users WHERE userID = ?;", (id,))
            num = float(cur.fetchone()[0])
            if num != 0:
                cur.execute("SELECT balance FROM Users WHERE userID=?;", (id,))
                balance = float(cur.fetchone()[0])
                return balance
            return 0

        