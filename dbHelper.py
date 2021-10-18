from flask import current_app, g
import hashlib
import os
import mysql.connector


def connectToDB():
    mydb = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password= os.getenv("DB_PASSWORD"),
        database="newData"
    )
    return mydb


def createUserTable():
    conn = connectToDB()
    print("Connected to DB")
    cur = conn.cursor()

    sql = """
        CREATE TABLE users (
            uid smallint(4) AUTO_INCREMENT,
            username varchar(50) UNIQUE,
            PRIMARY KEY (uid)
        ) ENGINE=InnoDB
    """
    cur.execute(sql)
    print("executed SQL statement")
    conn.commit()
    cur.close()
    conn.close()



def createListTable():
    conn = connectToDB()
    cur = conn.cursor()

    sql = """
        CREATE TABLE lists (
            uid smallint(4) AUTO_INCREMENT,
            name varchar(55),
            type varchar(5),
            author varchar(50),
            PRIMARY KEY (uid),
            FOREIGN KEY (author) 
                REFERENCES users(username)
        )ENGINE=InnoDB
    """
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


def createEntryTable():
    conn = connectToDB()
    cur = conn.cursor()

    sql = """
        CREATE TABLE entries (
            uid smallint(6) AUTO_INCREMENT,
            listId smallint(4) NOT NULL,
            name varchar(75),
            position smallint(6),
            image varchar(150),
            url varchar(150),
            notes varchar(500) DEFAULT "",
            rating varchar(2) DEFAULT "-",
            description text,
            PRIMARY KEY (uid),
            FOREIGN KEY (listId) 
                REFERENCES lists(uid)
                ON DELETE CASCADE
) ENGINE=InnoDB
    """
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


def insertUser(name):
    conn = connectToDB()

    cur = conn.cursor()


    sql = "INSERT INTO users(username) VALUES (%s)"
    data = (name,)
    cur.execute(sql, data)
    conn.commit()
    cur.close()
    conn.close()


def insertList(name, type, user):
    conn = connectToDB()

    cur = conn.cursor()

    sql = "INSERT INTO lists(name,type,author) VALUES (%s,%s,%s)"
    data = (name, type, user,)
    cur.execute(sql, data)
    conn.commit()
    cur.close()
    conn.close()


# Should i give it position%s or is the function to job to find where it should insert%s
def insertEntry(name, listId, position, imageURL, description):
    conn = connectToDB()

    cur = conn.cursor()

    sql = "INSERT INTO entries(name,listId,position, image) VALUES (%s,%s,%s,%s)"
    data = (name, listId, position, imageURL,)
    cur.execute(sql, data)
    conn.commit()
    cur.close()
    conn.close()

def getUser(username, password = None):
    
    conn = connectToDB()

    cur = conn.cursor()
    if password == None:
        sql = '''SELECT uid FROM users WHERE username = %s'''
        data = (username,)
    else:
        newPass = hashlib.sha1(password.encode("utf-8")).hexdigest()
        sql = '''SELECT uid FROM users WHERE username = %s AND password = %s'''
        data = (username,newPass,)

    cur.execute(sql,data)

    user = cur.fetchone()
    print("USER: ")
    print(user)

    cur.close()
    conn.close()
    if user == None:
        return ("Failure", "null")
    else:
        return ("Success", user[0])

def isNameTaken(username):
    conn = connectToDB()

    cur = conn.cursor()

    sql = '''SELECT uid FROM users WHERE username = %s'''

    data = (username,)

    cur.execute(sql,data)
    if len(cur.fetchall()) == 0:
        cur.close()
        conn.close()
        return False
    else:
        cur.close()
        conn.close()
        return True

def getUsers():
    conn = connectToDB()
    cur = conn.cursor()
    sql = '''SELECT username FROM users'''
    cur.execute(sql)
    users = cur.fetchall()
    formatted_users = []
    for x in users:
        formatted_users.append(x[0])
    cur.close()
    conn.close()
    return formatted_users

def getUserName(userId):
    conn = connectToDB()
    cur = conn.cursor()

    sql = """SELECT username from users where uid = %s"""
    data = (userId,)
    cur.execute(sql, data)
    user = cur.fetchone()[0]
    cur.close()
    conn.close()
    return user


def listExists(listName):
    conn = connectToDB()
    cur = conn.cursor()

    sql = """SELECT * FROM lists WHERE name = %s"""
    data = (listName,)
    cur.execute(sql, data)
    cur_lists = cur.fetchall()
    cur.close()
    conn.close()
    return len(cur_lists) != 0


def createNewListFromJson(jsonData):
    listName = jsonData["listName"]
    #userId = jsonData["userId"]
    author = jsonData['username']
    if listExists(listName) == False:
        insertList(listName, jsonData["genre"], author)
    else:
        return False
    return True


def removeList(listId):
    conn = connectToDB()
    cur = conn.cursor()

    sql = """DELETE FROM lists WHERE uid = %s """

    data = (listId,)
    cur.execute(sql, data)
    conn.commit()
    cur.close()
    conn.close()


def getEntries(listId):
    conn = connectToDB()
    cur = conn.cursor()

    sql = """ 
        SELECT uid, name, position, image, url, notes, rating, description
        FROM entries 
        WHERE listId = %s """
    data = (listId,)

    cur.execute(sql, data)

    entries = cur.fetchall()
    print("fetching...")
    cur.close()
    conn.close()
    return entries


def addEntry(listId, title, image, url, description = None):
    conn = connectToDB()
    cur = conn.cursor()

    sql = """ SELECT COUNT(listId) FROM entries WHERE listId = %s"""

    data = (listId,)
    # query to get the current amount of entries in list used for position
    cur.execute(sql, data)
    entryCount = cur.fetchone()[0] + 1

    # some entries might not have a description provided
    if description != None:
        sql = """ INSERT INTO entries(listId,name,position,image,url,description) VALUES (%s,%s,%s,%s,%s,%s)"""
        data = (listId, title, entryCount, image, url, description,)
    else:
        sql = """ INSERT INTO entries(listId,name,position,image,url) VALUES (%s,%s,%s,%s,%s)"""
        data = (listId, title, entryCount, image, url,)

    cur.execute(sql, data)
    conn.commit()
    cur.close()
    conn.close()


def removeEntry(entryId):
    conn = connectToDB()
    cur = conn.cursor()
    data = (entryId,)

    # current implementation idea: get position of deleted item and find all occurences where position > current
    # and subtract each position by 1
    getPositionSQL = """
        SELECT position, listId 
        FROM entries 
        WHERE uid = %s """

    cur.execute(getPositionSQL, data)
    entry = cur.fetchone()
    position = entry[0]
    listId = entry[1]
    print(position)

    sql = """DELETE FROM entries WHERE uid = %s """
    print("removing..")
    cur.execute(sql, data)

    updateSQL = """
        UPDATE entries 
        SET position = position - 1 
        WHERE position > %s AND listId = %s"""
    data = (position, listId,)
    print("updating finished")
    cur.execute(updateSQL, data)
    conn.commit()
    cur.close()
    conn.close()


def getEntryCount(listId):
    conn = connectToDB()
    cur = conn.cursor()

    sql = """SELECT COUNT(*) FROM entries WHERE listId = %s"""

    data = (listId,)
    cur.execute(sql, data)
    totalCount = cur.fetchone()[0]
    cur.close()
    conn.close()
    return totalCount


def getListInfo(listId):
    conn = connectToDB()
    cur = conn.cursor()

    sql = '''SELECT * FROM lists WHERE uid = %s'''
    data = (listId,)
    cur.execute(sql,data)

    listInfo = cur.fetchone()
    print(listInfo)

    cur.close()
    conn.close()
    return listInfo

def changeOrder(listId, entryId, position, direction):
    if direction == "down" and position == getEntryCount(listId):
        print("already at bottom")
    elif direction == "up" and position == 1:
        print("already at top")
    else:
        conn = connectToDB()
        cur = conn.cursor()
        # Also need to make sure they update their swapping partner too
        if direction == "up":

            updateSQL = """
                UPDATE entries 
                SET position = position + 1 
                WHERE position = %s AND listId = %s"""
            data = (position - 1, listId,)
            cur.execute(updateSQL, data)

            sql = """
                UPDATE entries 
                SET position = position - 1 
                WHERE uid = %s"""
            data = (entryId,)
            cur.execute(sql, data)
            conn.commit()
        else:
            updateSQL = """
                UPDATE entries 
                SET position = position - 1 
                WHERE position = %s AND listId = %s"""
            data = (position + 1, listId,)
            cur.execute(updateSQL, data)

            sql = """
                UPDATE entries 
                SET position = position + 1 
                WHERE uid = %s"""
            data = (entryId,)
            cur.execute(sql, data)
            conn.commit()
        cur.close()
        conn.close()


def updateEntry(entryId, note, rating):
    conn = connectToDB()
    cur = conn.cursor()
    print(f"updating: {entryId} with info: \n {note} and {rating}")
    print(f"{type(rating)}")
    sql = """
        UPDATE entries 
        SET notes = %s, rating = %s
        WHERE uid = %s"""
    data = (note, rating, entryId,)

    cur.execute(sql, data)
    conn.commit()
    cur.close()
    conn.close()


def populateDB():
    createUserTable()
    createListTable()
    createEntryTable()


def dropTables():
    conn = connectToDB()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS entries")
    cursor.execute("DROP TABLE IF EXISTS lists")
    cursor.execute("DROP TABLE IF EXISTS users")
    conn.commit()
    cursor.close()
    print("finished dropping tables")
    conn.close()


def testDB():
    insertList("Marvel", "movie")
    insertEntry(
        "SpiderMan",1,1,"https://image.tmdb.org/t/p/w92/gh4cZbhZxyTbgxQPxD0dOudNPTn.jpg",
    )
    insertEntry(
        "Iron Man",1,2,"https://image.tmdb.org/t/p/w92/78lPtwv72eTNqFW9COBYI0dWDJa.jpg",
    )


def getLists(listType):
    conn = connectToDB()
    cur = conn.cursor()
    if listType == "All":
        sql = """SELECT * FROM lists"""
    elif listType == "Movies":
        sql = """ SELECT * FROM lists WHERE type = 'movie' """
    elif listType == "TV":
        sql = """ SELECT * FROM lists WHERE type = 'tv' """
    else:
        sql = """ SELECT * FROM lists WHERE type = 'anime' """

    cur.execute(sql)
    lists = cur.fetchall()

    lists = lists[::-1]

    cur.close()
    conn.close()

    return lists

def getUserLists(userid):
    conn = connectToDB()
    cur = conn.cursor()

    sql = """SELECT * FROM lists WHERE author = %s"""

    data = (userid,)

    cur.execute(sql,data)
    lists = cur.fetchall()

    lists = lists[::-1]

    cur.close()
    conn.close()

    return lists

if __name__ == "__main__":
    #dropTables()
    #populateDB()
    #getListInfo(1)

    #dropTables()
    #populateDB()
    #print(getUsers())
    #createUserTable()
    #getListInfo(1)
    #insertUser('newUser')
    #insertUser('test')
    insertUser('BAD guy!')
    #addEntry(2,'NEWER TEST MOVIE','http://www.thisisanImage.com','http:/www.testURL.com')
    #removeList (1)