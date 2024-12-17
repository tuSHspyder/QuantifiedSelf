from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
  __tablename__='user'
  userid=db.Column(db.Integer, primary_key=True,autoincrement=True)
  username=db.Column(db.String, unique=True, nullable=False)
  track=db.relationship("Tracker")

class Tracker(db.Model):
  __tablename__='trackers'
  tid=db.Column(db.Integer, primary_key=True,autoincrement=True)
  tname=db.Column(db.String, nullable=False)
  tdescription=db.Column(db.String)
  ttype=db.Column(db.String, nullable=False)
  tsetting=db.Column(db.String)
  userid=db.Column(db.Integer,db.ForeignKey("user.userid"))
  log=db.relationship("Log", cascade="all,delete-orphan")

class Log(db.Model):
  __tablename__='logs'
  logid=db.Column(db.Integer, primary_key=True,autoincrement=True)
  time=db.Column(db.String, nullable=False)
  tracker=db.Column(db.String, nullable=False)
  value=db.Column(db.String, nullable=False)
  note=db.Column(db.String, nullable=False)
  tid=db.Column(db.Integer,db.ForeignKey("trackers.tid"))

