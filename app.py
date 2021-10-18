import dbHelper
from flask import Flask, request, jsonify, Response
from flask_cors import CORS, cross_origin
import json
import scraper

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.debug= True

#returns all lists created in DB (for homepage)
@app.route('/lists', methods = ["GET"])
@cross_origin()
def getLists():

    listType = request.args.get("cat")
    lists = dbHelper.getLists(listType)
    print(f"lists {lists} for {listType}")
    formatted_lists = [{
        "id": list[0],
        "title": list[1],
        "type": list[2],
        "author": list[3]
    } for list in lists]

    resp = jsonify(formatted_lists)
    resp.status_code = 200
    return resp

@app.route('/userPage', methods = ["GET"])
@cross_origin()
def getUserLists():
    
    userId = int(request.args.get('userId'))
    
    name = dbHelper.getUserName(userId)
    lists = dbHelper.getUserLists(userId)
    
    formatted_lists = [{
        "id": list[0],
        "title": list[1],
        "type": list[2]
    } for list in lists]

    resp = jsonify({"lists": formatted_lists, "name": name})
    resp.status_code = 200
    return resp

@app.route('/profPage', methods = ["GET"])
@cross_origin()
def getUserListsFromName():
    
    name = (request.args.get('uname'))
    
    
    lists = dbHelper.getUserLists(name)
    
    formatted_lists = [{
        "id": list[0],
        "title": list[1],
        "type": list[2]
    } for list in lists]

    resp = jsonify({"lists": formatted_lists, "name": name})
    resp.status_code = 200
    return resp

@app.route('/getUsers', methods = ['GET'])
@cross_origin()
def getUsers():
    users = dbHelper.getUsers()

    return jsonify({"users": users})

#method to create a new list
@app.route('/createList', methods = ["POST"])
@cross_origin()
def createList():
    data = json.loads(request.data.decode('UTF-8'))

    print(f"in function data: {data}")
    didInsert = dbHelper.createNewListFromJson(data)
    if didInsert:
        resp = jsonify({'status_code': 200})
    else:
        resp = jsonify({'status_code': 404})

    return resp

@app.route('/removeList', methods = ["POST"])
@cross_origin()
def removeList():
    data = json.loads(request.data.decode('UTF-8'))
    listId = data['listId']
    dbHelper.removeList(listId)
    resp = jsonify({'status_code': 200})
    return resp

@app.route("/getListInfo",methods=["GET"])
@cross_origin()
def getListInfo():
    
    listId = request.args['listId']

    listInfo = dbHelper.getListInfo(listId)

    resp = jsonify({'title': listInfo[1], 'type': listInfo[2], 'author': listInfo[3]})

    return resp

@app.route('/getListEntries', methods=["GET"])
@cross_origin()
def getListEntries():
    
    listId = request.args['listId']
    listEntries = dbHelper.getEntries(listId)

    formatted_entries = [{
        "id": entry[0],
        "title": entry[1],
        "position": entry[2],
        "image": entry[3],
        "url": entry[4],
        "notes": entry[5],
        "rating": entry[6],
        "desc": entry[7]
    } for entry in listEntries]
    
    #sorts the array so they're in order of possition
    formatted_entries.sort(key= lambda x: x['position'])
    resp = jsonify(formatted_entries)
    resp.status_code = 200
    return resp

@app.route('/addEntry', methods=["POST"])
@cross_origin()
def addEntry():
    data = json.loads(request.data.decode('UTF-8'))
    listId = data['listId']
    listType = data['listType']
    #make it pass the list type? so that if its anime it knows it needs to get description
    entryName = data['title']
    entryImage = data['img']
    entryURL = data['url']

    if listType == "anime":
        entryDesc = scraper.getDesc(entryURL)
    else:
        entryDesc = data['desc']


    dbHelper.addEntry(listId,entryName,entryImage, entryURL, entryDesc)
    resp = jsonify({'status_code': 200})
    return resp

@app.route('/removeEntry', methods=["POST"])
#make removeEntry return new array 
@cross_origin()
def removeEntry():
    data = json.loads(request.data.decode('UTF-8'))
    entryId = data['entryId']
    listId = data['listId']

    dbHelper.removeEntry(entryId)
    newList = dbHelper.getEntries(listId)
    print(f"new list after deletion: {newList}")
    resp = jsonify({'entries': newList})
    resp.status_code = 200
    return resp

@app.route('/changeOrder', methods=["POST"])
@cross_origin()
def changeOrder():
    data = json.loads(request.data.decode('UTF-8'))
    entryId = data['entryId']
    listId = data['listId']
    direction = data['direction']
    position = data['position']
    #I think Entry ID is UID but IDK for sure
    print(f"entry ID: {entryId} listId: {listId}, position: {position} direction: {direction}")
    dbHelper.changeOrder(listId, entryId, position, direction)
    resp = jsonify({'status_code': 200})
    return resp

@app.route('/searchAnime', methods=["GET"])
@cross_origin()
def getAnimeSuggestions():
    if 'q' in request.args:
        query = request.args['q']
    resp = jsonify(scraper.getAnimeSearchSuggestions(query))
    resp.status_code = 200
    return resp

@app.route('/editEntry', methods=["PUT"])
@cross_origin()
def editEntry():
    data = json.loads(request.data.decode('UTF-8'))
    print(f"DATA: {data}")
    note = data['newNote']
    #if position and rating dont change then dont use them for now we're assuming they always change
    rating = data['rating']
    entryId = data['entryId']

    
    dbHelper.updateEntry(entryId,note, rating)
    resp = jsonify({'status_code': 200}) 
    return resp

@app.route('/login', methods=["POST"])
@cross_origin()
def login():
    data = json.loads(request.data.decode('UTF-8'))
    userName = data['userName']
    password = data['password']
    
    loginStatus = dbHelper.getUser(userName,password)
    #checks if user gave correct password and name
    if loginStatus[0] == "Success":
        resp = jsonify({'userId': loginStatus[1], 'username': userName, 'status_code': 200})
    else:
        resp=jsonify({'status_code': 406})

    return resp



@app.route('/signUp', methods=["POST"])
@cross_origin()
def signup():
    print("receiveing a call to signup")
    data = json.loads(request.data.decode('UTF-8'))
    userName = data['userName']

    # checks if userName is in use
    if dbHelper.isNameTaken(userName) == False:
        dbHelper.insertUser(userName)
        userId = dbHelper.getUser(userName)[1]
        resp = jsonify({'userId': userId, 'username': userName, 'status_code': 200})
    else:
        resp=jsonify({'status_code': 406})

    return resp

@app.route('/getUser', methods=["GET"])
@cross_origin()
def getUser():
    uid = request.args['userId']
    
    # checks if userName is in use
    uname = dbHelper.getUserName(uid)

    resp = jsonify({'userId': uid, 'username': uname})
    resp.status_code = 200
    return resp
