import os
import json
import random

from app import app, db, DB_FILE

from models import *

# creating the user josh
def create_user():
    josh = User("Josh", "20060616")
    db.session.add(josh)
    db.session.commit()



# loading JSON data in to our database
def load_data():
    with open("clubs.json") as f:
        clubs = json.load(f)

        for curr in clubs:
            name = curr["name"]
            code = curr["code"]
            description = curr["description"]
            club = Club(name, code, description)
            db.session.add(club)

            # tags require special treatment, since they are relational classes,
            # I will first check if the tag object had been created yet
            for tag_name in curr["tags"]:
                tag = Tag.query.filter_by(name=tag_name).first()
                if tag is None:
                    tag = Tag(name = tag_name)
                    db.session.add(tag)
                club.tags.append(tag)
    db.session.commit()
    print("Done.")


# a function to debug easily, printing out every information stored in our database.
# I didn't use the build in debug because printing is just clearer in this case
def debug():
    clubs = Club.query.all()
    for club in clubs:
        print(club.name)
        print(club.code)
        print(club.description)
        for tag in club.tags:
            print(tag.name)
        print("/n")


# No need to modify the below code.
# I added a debug section, that's it
if __name__ == "__main__":
    # Delete any existing database before bootstrapping a new one.
    LOCAL_DB_FILE = "instance/" + DB_FILE
    if os.path.exists(LOCAL_DB_FILE):
        os.remove(LOCAL_DB_FILE)

    with app.app_context():
        db.create_all()
        create_user()
        load_data()
        debug()
