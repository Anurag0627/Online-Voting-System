from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# -------------------
# VOTER TABLE
# -------------------
class Voter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # will store hashed password
    has_voted = db.Column(db.Boolean, default=False)

# -------------------
# CANDIDATE TABLE
# -------------------
class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    votes = db.Column(db.Integer, default=0)

# -------------------
# VOTE RECORD TABLE
# -------------------
class VoteRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voter_id = db.Column(db.Integer, db.ForeignKey('voter.id'))
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'))


