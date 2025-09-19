from sqlalchemy import ForeignKey

from app import db

# Your database models should go here.
# Check out the Flask-SQLAlchemy quickstart for some good docs!
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/


#associated table recording the many to many relationship between user and clubs for favourites
user_favourites = db.Table('user_favourites',
                           db.Column('user_name', db.String, db.ForeignKey("user.username"), primary_key=True),
                           db.Column('club_code', db.String, db.ForeignKey("club.code"), primary_key=True)
                           )

#associated table recording the many to many relationship between clubs and tags
club_tags = db.Table('club_tags',
                           db.Column('tag_name', db.String, db.ForeignKey("tag.name"), primary_key=True),
                           db.Column('club_code', db.String, db.ForeignKey("club.code"),primary_key=True)
                           )

#associated table recording the many to many relationship between clubs and user for membership
memberships = db.Table('membership',
                  db.Column('user_name', db.String, db.ForeignKey("user.username"), primary_key=True),
                  db.Column('club_code', db.String, db.ForeignKey("club.code"), primary_key=True)
                           )

# the model for clubs
class Club(db.Model):
    __tablename__ = "club"
    code = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    #storing tags in another model, so we can create the associate tables
    tags = db.relationship(
        "Tag",
        secondary=club_tags,
        backref="clubs"
    )

    #we ought to create another model for user anyways
    fans = db.relationship(
        "User",
        secondary=user_favourites,
        backref="favourites"
    )

    # another relationship to keep track which user in the club
    members = db.relationship(
        "User",
        secondary=memberships,
        backref="memberof"
    )

    def __init__(self, name,code,description):
        self.name = name
        self.code = code
        self.description = description

# the model for tags
class Tag(db.Model):
    __tablename__ = "tag"
    name = db.Column(db.String, primary_key=True)

    def __init__(self, name):
        self.name = name


# the model for User
class User(db.Model):
    __tablename__ = "user"
    username = db.Column(db.String, primary_key=True)

    def __init__(self, username):
        self.username = username
