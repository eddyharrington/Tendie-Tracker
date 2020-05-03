import os
import json
import requests
import calendar
import copy
import config

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///budget.db")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        # Query DB for all existing user names and make sure new username isn't already taken
        username = request.form.get("username")
        existingUsers = db.execute(
            "SELECT username FROM users WHERE LOWER(username) = :username", username=username.lower())
        if existingUsers:
            return render_template("register.html", username=username)

        # Ensure username was submitted - server side validation (javascript should prevent from reaching this in most cases)
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted - server side validation (javascript should prevent from reaching this in most cases)
        password = request.form.get("password")
        if not password:
            return apology("must provide password", 403)

        # Ensure confirmation is submitted - server side validation (javascript should prevent from reaching this in most cases)
        confirmation = request.form.get("confirmation")
        if not confirmation:
            return apology("must provide a password confirmation", 403)

        # Ensure confirmation matches password - server side validation (javascript should prevent from reaching this in most cases)
        if password != confirmation:
            return apology("your password and confirmation must be the same", 403)

        # Insert user into the database
        hashedPass = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hashedPass)",
                   username=username, hashedPass=hashedPass)

        # Auto-login the user after creating their username and redirect to home page
        rows = db.execute(
            "SELECT * FROM users WHERE username = :username", username=username)
        session["user_id"] = rows[0]["id"]

        # Create default spending categories for user (i.e. first 8 entries in 'categories' table)
        db.execute("INSERT INTO userCategories (category_id, user_id) VALUES (1, :usersID), (2, :usersID), (3, :usersID), (4, :usersID), (5, :usersID), (6, :usersID), (7, :usersID), (8, :usersID)",
                   usersID=session["user_id"])

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show dashboard of budget/expenses"""

    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
