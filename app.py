from flask import Flask, request, jsonify, render_template, session, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# -----------------------------------
# FLASK SETUP
# -----------------------------------

app = Flask(__name__)
app.secret_key = "this_is_a_demo_secret_change_me"

# Admin static credentials
ADMIN_USERNAME = "admin@gmail.com"
ADMIN_PASSWORD = "admin123"

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///voting.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# -----------------------------------
# DATABASE MODELS
# -----------------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    has_voted = db.Column(db.Boolean, default=False)


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    position = db.Column(db.String(100))
    votes = db.Column(db.Integer, default=0)


# Create DB tables
with app.app_context():
    db.create_all()


# -----------------------------------
# USER REGISTRATION
# -----------------------------------

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    hashed = generate_password_hash(password)
    user = User(name=name, email=email, password=hashed)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered"})


# -----------------------------------
# USER LOGIN
# -----------------------------------

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not check_password_hash(user.password, password):
        return jsonify({"error": "Incorrect password"}), 400

    return jsonify({"message": "Login successful", "user_id": user.id})


# -----------------------------------
# USER VOTING
# -----------------------------------

@app.route("/vote", methods=["POST"])
def vote():
    data = request.json
    user_id = data.get("user_id")
    candidate_id = data.get("candidate_id")

    user = User.query.get(user_id)
    candidate = Candidate.query.get(candidate_id)

    if not user:
        return jsonify({"error": "User not found"}), 404
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404
    if user.has_voted:
        return jsonify({"error": "Already voted"}), 400

    user.has_voted = True
    candidate.votes += 1

    db.session.commit()
    return jsonify({"message": "Vote submitted"})


# -----------------------------------
# WEBSITE PAGES
# -----------------------------------

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register_page")
def register_page():
    return render_template("register.html")


@app.route("/login_page")
def login_page():
    return render_template("login.html")


@app.route("/results_page")
def results_page():
    candidates = Candidate.query.all()
    return render_template("results.html", candidates=candidates)


@app.route("/vote_page")
def vote_page():
    candidates = Candidate.query.all()
    return render_template("vote.html", candidates=candidates)


# -----------------------------------
# ADMIN LOGIN
# -----------------------------------

@app.route("/admin_login_page")
def admin_login_page():
    return render_template("admin_login.html")


@app.route("/admin_login", methods=["POST"])
def admin_login():
    username = request.form.get("username")
    password = request.form.get("password")

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session["is_admin"] = True
        session["admin_id"] = 1  # Static admin ID
        return redirect("/admin_dashboard/1")

    return render_template("admin_login.html", error="Invalid credentials")


# -----------------------------------
# ADMIN DASHBOARD
# -----------------------------------

@app.route("/admin_dashboard/<int:admin_id>")
def admin_dashboard(admin_id):

    if not session.get("is_admin"):
        return redirect("/admin_login_page")

    # Admin is not in DB → create temporary object
    class Admin:
        id = 1
        name = "Administrator"

    admin_user = Admin()

    candidates = Candidate.query.all()
    users = User.query.all()
    voted_count = User.query.filter_by(has_voted=True).count()

    return render_template(
        "admin_dashboard.html",
        user=admin_user,
        candidates=candidates,
        users=users,
        voted_count=voted_count
    )


# -----------------------------------
# ADMIN: ADD CANDIDATE
# -----------------------------------

@app.route("/admin_add_candidate_page")
def admin_add_candidate_page():
    if not session.get("is_admin"):
        return redirect("/admin_login_page")
    return render_template("admin_add_candidate.html")


@app.route("/admin_add_candidate", methods=["POST"])
def admin_add_candidate():
    if not session.get("is_admin"):
        return redirect("/admin_login_page")

    name = request.form.get("name")
    position = request.form.get("position")

    if not name or not position:
        return "Name and position required", 400

    new_cand = Candidate(name=name, position=position)
    db.session.add(new_cand)
    db.session.commit()

    return redirect("/admin_view_candidates")


# -----------------------------------
# ADMIN: VIEW / DELETE CANDIDATES
# -----------------------------------

@app.route("/admin_view_candidates")
def admin_view_candidates():
    if not session.get("is_admin"):
        return redirect("/admin_login_page")

    candidates = Candidate.query.all()
    return render_template("admin_view_candidates.html", candidates=candidates)


@app.route("/delete_candidate/<int:id>")
def delete_candidate(id):
    if not session.get("is_admin"):
        return redirect("/admin_login_page")

    candidate = Candidate.query.get(id)
    if candidate:
        db.session.delete(candidate)
        db.session.commit()

    return redirect("/admin_view_candidates")


# -----------------------------------
# ADMIN: RESET VOTES
# -----------------------------------

@app.route("/admin_reset_votes", methods=["POST"])
def admin_reset_votes():
    if not session.get("is_admin"):
        return redirect("/admin_login_page")

    for c in Candidate.query.all():
        c.votes = 0
    for u in User.query.all():
        u.has_voted = False

    db.session.commit()

    return redirect("/admin_dashboard/1")


# -----------------------------------
# ADMIN LOGOUT
# -----------------------------------

@app.route("/admin_logout")
def admin_logout():
    session.clear()
    return redirect("/admin_login_page")


# -----------------------------------
# RUN SERVER
# -----------------------------------

if __name__ == "__main__":
    app.run(debug=True)
