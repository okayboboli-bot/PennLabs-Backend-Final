from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

DB_FILE = "clubreview.db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_FILE}"
db = SQLAlchemy(app)

from models import *


@app.route("/")
def main():
    return "Welcome to Penn Club Review!"


@app.route("/api")
def api():
    return jsonify({"message": "Welcome to the Penn Club Review API!."})

# not sure do we need to return all information or just names, so I made two
@app.route("/api/clubs", methods=["GET"])
def get_all_clubs():
    #getting all Club objs
    clubs = Club.query.all()

    # creating a list to store the club names
    clublist = []
    for club in clubs:
        clublist.append(club.name)

    #jsonify and output
    return jsonify(clublist)

@app.route("/api/clubsdetail", methods=["GET"])
def get_all_clubs_obj():
    #getting all Club objs
    clubs = Club.query.all()

    #creating list to store
    clublist = []
    for club in clubs:

        #making a dictionary for each club and adding them to the final list
        diction = {}
        diction["name"] = club.name
        diction["code"] = club.code
        diction["description"] = club.description
        diction["tags"] = [tag.name for tag in club.tags]
        diction["fans"] = [user.username for user in club.fans]
        diction["members"] = [user.username for user in club.members]
        clublist.append(diction)

    #return the jsonified list of dictionaries
    return jsonify(clublist)

@app.route("/api/users/<string:username>", methods=["GET"])
def get_user_profile(username):

    #creating a dictionary to store info of user
    userdict = {}

    #find the user obj
    user = User.query.filter_by(username=username).first()

    #error message if no such user
    if user is None:
        return jsonify({"message": "No user found!"})

    #adding info and jsonify the dictionary
    userdict["username"] = user.username
    userdict["favourites"] = [club.name for club in user.favourites]
    userdict["memberof"] = [club.name for club in user.memberof]
    return jsonify(userdict)

@app.route("/api/clubs/<string:clubname>", methods=["GET"])
def serach_club(clubname):

    #taking all clubs that contains the word, case insensitve
    clubs = Club.query.filter(Club.name.ilike(f"%{clubname}%")).all()

    #making into python list to jasonifiable
    clublist = [club.name for club in clubs]

    #message if no clubs is found
    if len(clublist) == 0:
        return jsonify({"message": "No club found!"})
    return jsonify(clublist)

@app.route("/api/clubs", methods=["POST"])
def create_club():

    #taking extra information from the call
    data = request.get_json()
    newclubname = data.get("name")
    clubcode = data.get("code")
    clubdescription = data.get("description")
    clubtags = data.get("tags")

    #check if we are missing one of the information
    if (newclubname is None or
            clubcode is None or
    clubdescription is None or clubtags is None):
        return jsonify({"message": "Not a valid club"})


    #error message if we have the same clubname and clubcode, since they can't be the same
    if Club.query.filter_by(name = newclubname).first() is not None:
        return jsonify({"message": "Clubname already exists!"})
    if Club.query.filter_by(code = clubcode).first() is not None:
        return jsonify({"message": "Clubcode already exists!"})

    #creating the club
    club = Club(newclubname, clubcode, clubdescription)
    db.session.add(club)


    #adding the clubtags, checking each time do we need to create a new tag obj
    for clubtag in clubtags:
        tag = Tag.query.filter_by(name=clubtag).first()
        if tag is None:
            tag = Tag(name=clubtag)
            db.session.add(tag)
        club.tags.append(tag)
    db.session.commit()

    #success message
    return jsonify({"message": "successfully created club"})


#helper for one user one club interactions, fav, join, quit
def helper(types, name):
    # getting the extra information
    data = request.get_json()
    username = data.get("username")

    # check if we received a username
    if username is None:
        return jsonify({"message": "No username found!"})

    # getting and checking if there is club looking for
    club = Club.query.filter_by(name=name).first()
    if club is None:
        return jsonify({"message": "Club not found!"})

    # getting and checking if there is the user we are looking for
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify({"message": "No user found!"})

    if types == "favourite":
        table = user.favourites
        if club in table:
            table.remove(club)
            db.session.commit()
            return jsonify(
                {"message": "successfully unfavourited club, now " + username + " have " + str(len(user.favourites))})
        table.append(club)
        db.session.commit()
        return jsonify(
            {"message": "successfully favourited club, now " + username + " have " + str(len(user.favourites))})
    elif types == "join":
        table = club.members
        if user in table:
            return jsonify({"message": "user already in club"})
        table.append(user)
        db.session.commit()
        return jsonify({"message": "successfully joined club, now " + name + " have " + str(len(club.members))})
    elif types == "quit":
        table = club.members
        if user not in table:
            return jsonify({"message": "user not in club"})
        table.remove(user)
        db.session.commit()
        return jsonify({"message": "successfully exited club, now " + name + " have " + str(len(club.members))})
    else:
        return jsonify({"message": "Invalid type"})

@app.route("/api/clubs/<string:name>/favourite", methods=["POST"])
def favourite_club(name):
    return helper("favourite", name)

@app.route("/api/clubs/<string:name>/join", methods=["POST"])
def join_club(name):
    return helper("join", name)

@app.route("/api/clubs/<string:name>/quit", methods=["POST"])
def quit_club(name):
    return helper("quit", name)

@app.route("/api/clubs/<string:code>/modify", methods=["PATCH"])
def modify_club(code):

    #obtain extra data
    data = request.get_json()

    #finding the club through code, as we might edit its username
    club = Club.query.filter_by(code=code).first()
    if club is None:
        return jsonify({"message": "Club not found!"})

    #obtain extra data
    newclubname = data.get("name")
    newclubdescription = data.get("description")
    newclubtags = data.get("tags")


    #if the newclubname is given, and we don't have the name yet, we change the name
    if newclubname is not None and Club.query.filter_by(name=newclubname).first() is None:
        club.name = newclubname

    # if the newdescription is given, change it
    if newclubdescription is not None:
        club.description = newclubdescription

    #if new tags are give, we remove the old one and again for each tag check if it has been created yet
    if newclubtags is not None:
        club.tags.clear()
        for clubtag in newclubtags:
            tag = Tag.query.filter_by(name=clubtag).first()
            if tag is None:
                tag = Tag(name=clubtag)
                db.session.add(tag)
            club.tags.append(tag)

    #commit and result success message
    db.session.commit()
    return jsonify({"message": "successfully modified club"})

@app.route("/api/tags", methods=["GET"])
def club_withtag_foreach():

    #creatign dictionary to jsonify
    temp_dict = {}

    # for each tag in all the tags, we output the amount of clubs we have for the tag
    tags = Tag.query.all()
    for tag in tags:
        temp_dict[tag.name] = len(tag.clubs)


    return jsonify(temp_dict)


if __name__ == "__main__":
    app.run()
