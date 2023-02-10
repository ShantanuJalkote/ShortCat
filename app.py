from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///shortcut.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show list of shortcuts"""
    userid = session["user_id"]

    user_shortcut_db = db.execute("SELECT name, link, logo FROM shortcuts WHERE userid=?", userid)

    return render_template("index.html", data=user_shortcut_db)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for email
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        name = rows[0]["username"]

        #flash welcome message
        flash(f"Welcome Back, {name} !")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 400)

        if not request.form.get("email"):
            return apology("must provide email", 400)

        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)

        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("password and confirmation do not match", 400)

        # Query database for username and email
        email_rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))
        username_rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("email"))

        # Ensure username exists
        if len(username_rows) == 1:
            return apology("Username already exists", 400)

        # Ensure email exists
        if len(email_rows) == 1:
            return apology("Email already exists", 400)

        # adding data into the database
        db.execute("INSERT INTO users(username, email, hash) VALUES(?, ?, ?)",request.form.get("username"), request.form.get("email"), generate_password_hash(request.form.get("password")))

        rows1 = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))
        # Remember which user has logged in
        session["user_id"] = rows1[0]["id"]

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add shortcut"""
    if request.method == "GET":
        return render_template("add.html")

    else:
        userid = session["user_id"]
        link = request.form.get("url")
        name = request.form.get("name")

        #if no link inputed
        if not link:
            return apology("No Url Inputed", 400)

        #if no name inputed
        if not name:
            return apology("No name Inputed", 400)

        logo_link = f"https://www.google.com/s2/favicons?sz=64&domain_url={link}"

        #insert shortcut
        db.execute("INSERT INTO shortcuts (name, link, userid, logo) VALUES(?, ?, ?, ?)", name, link, userid, logo_link)

        return redirect("/")


@app.route("/remove", methods=["GET", "POST"])
@login_required
def remove():
    """Add cash to total"""
    if request.method == "GET":
        userid = session["user_id"]
        user_shortcuts = db.execute("SELECT name FROM shortcuts WHERE userid=?", userid)
        return render_template("remove.html", shortcuts=[row["name"] for row in user_shortcuts])

    else:
        shortcut = request.form.get("shortcut")

        # if no shortcut inputed
        if not shortcut:
            return apology("shortcut does not exist", 400)

        # get the userid of shortcut to be deleted
        db.execute("DELETE FROM shortcuts WHERE name=?", shortcut)

        flash("Shortcut Removed!")

        return redirect("/")
