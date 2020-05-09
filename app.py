import os
import json
import requests
import copy
import config
import tendie_dashboard
import tendie_expenses
import tendie_budgets
import tendie_categories

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, usd

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

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///budget.db")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST
    if request.method == "POST":
        # Query DB for all existing user names and make sure new username isn't already taken
        username = request.form.get("username").strip()
        existingUsers = db.execute(
            "SELECT username FROM users WHERE LOWER(username) = :username", username=username.lower())
        if existingUsers:
            return render_template("register.html", username=username)

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        password = request.form.get("password")
        if not password:
            return apology("must provide password", 403)

        # Insert user into the database
        hashedPass = generate_password_hash(password)
        newUserID = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hashedPass)",
                               username=username, hashedPass=hashedPass)

        # Create default spending categories for user
        db.execute("INSERT INTO userCategories (category_id, user_id) VALUES (1, :usersID), (2, :usersID), (3, :usersID), (4, :usersID), (5, :usersID), (6, :usersID), (7, :usersID), (8, :usersID)",
                   usersID=newUserID)

        # Auto-login the user after creating their username
        session["user_id"] = newUserID

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST
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

    # User reached route via GET
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

    # User reached route via GET
    if request.method == "GET":
        # Initialize metrics to None to render the appropriate UX if data does not exist yet for the user
        expenses_year = None
        expenses_month = None
        expenses_week = None
        expenses_last5 = None
        spending_week = []
        spending_month = []

        # Get the users spend categories (for quick expense modal)
        categories = tendie_categories.getSpendCategories(session["user_id"])

        # Get todays date (for quick expense modal)
        date = datetime.today().strftime('%Y-%m-%d')

        # Get the users income
        income = tendie_dashboard.getIncome(session["user_id"])

        # Get current years total expenses for the user
        expenses_year = tendie_dashboard.getTotalSpend_Year(session["user_id"])

        # Get current months total expenses for the user
        expenses_month = tendie_dashboard.getTotalSpend_Month(
            session["user_id"])

        # Get current week total expenses for the user
        expenses_week = tendie_dashboard.getTotalSpend_Week(session["user_id"])

        # Get last 5 expenses for the user
        expenses_last5 = tendie_dashboard.getLastFiveExpenses(
            session["user_id"])

        # Get every budgets spent/remaining for the user
        budgets = tendie_dashboard.getBudgets(session["user_id"])

        # Get weekly spending for the user
        weeks = tendie_dashboard.getLastFourWeekNames()
        spending_week = tendie_dashboard.getWeeklySpending(
            weeks, session["user_id"])

        # Get monthly spending for the user (for the current year)
        spending_month = tendie_dashboard.getMonthlySpending(
            session["user_id"])

        # TODO consider passing additional vars to the template that has strings formatted for the charts. E.g. javascript needs months/data in an array,
        # but due to jinja looping it makes the HTML doc render really messy with a lot of spaces. Might be better to just pass a single string for those charts.

        # Get spending trends for the user
        spending_trends = tendie_dashboard.getSpendingTrends(
            session["user_id"])

        return render_template("index.html", categories=categories, date=date, income=income, expenses_year=expenses_year, expenses_month=expenses_month, expenses_week=expenses_week, expenses_last5=expenses_last5,
                               budgets=budgets, spending_week=spending_week, spending_month=spending_month, spending_trends=spending_trends)

    # User reached route via POST
    else:
        # Get all of the expenses provided from the HTML form
        formData = list(request.form.items())

        # Add expenses to the DB for user
        expenses = tendie_expenses.addExpenses(formData, session["user_id"])

        # Redirect to results page and render a summary of the submitted expenses
        return render_template("expensed.html", results=expenses)


@app.route("/expenses", methods=["GET"])
@login_required
def expenses():
    """Manage expenses"""

    return render_template("expenses.html")


@app.route("/addexpenses", methods=["GET", "POST"])
@login_required
def addexpenses():
    """Add new expense(s)"""

    # User reached route via POST
    if request.method == "POST":
        # Get all of the expenses provided from the HTML form
        formData = list(request.form.items())

        # Add expenses to the DB for user
        expenses = tendie_expenses.addExpenses(formData, session["user_id"])

        # Redirect to results page and render a summary of the submitted expenses
        return render_template("expensed.html", results=expenses)

    # User reached route via GET
    else:
        # Get the users spend categories
        categories = tendie_categories.getSpendCategories(session["user_id"])

        # Render expense page
        date = datetime.today().strftime('%Y-%m-%d')
        return render_template("addexpenses.html", categories=categories, date=date)


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    """Show history of expenses or let the user update existing expense"""

    # User reached route via GET
    if request.method == "GET":
        # Get all of the users expense history ordered by submission time
        history = tendie_expenses.getHistory(session["user_id"])

        # Get the users spend categories
        categories = tendie_categories.getSpendCategories(session["user_id"])

        return render_template("history.html", history=history, categories=categories, isDeleteAlert=False)

    # User reached route via POST
    else:
        # Initialize users action
        userHasSelected_deleteExpense = False

        # Determine what action was selected by the user (button/form trick from: https://stackoverflow.com/questions/26217779/how-to-get-the-name-of-a-submitted-form-in-flask)
        if "btnDeleteConfirm" in request.form:
            userHasSelected_deleteExpense = True
        elif "btnSave" in request.form:
            userHasSelected_deleteExpense = False
        else:
            return apology("Doh! Spend Categories is drunk. Try again!")

        # Get the existing expense record ID from the DB and build a data structure to store old expense details
        oldExpense = tendie_expenses.getExpense(
            request.form, session["user_id"])

        # Make sure an existing record was found otherwise render an error message
        if oldExpense["id"] == None:
            return apology("The expense record you're trying to update doesn't exist")

        # Delete the existing expense record
        if userHasSelected_deleteExpense == True:

            # Delete the old record from the DB
            deleted = tendie_expenses.deleteExpense(
                oldExpense, session["user_id"])
            if not deleted:
                return apology("The expense was unable to be deleted.")

            # Get the users expense history, spend categories, and then render the history page w/ delete alert
            history = tendie_expenses.getHistory(session["user_id"])
            categories = tendie_categories.getSpendCategories(
                session["user_id"])
            return render_template("history.html", history=history, categories=categories, isDeleteAlert=True)

        # Update the existing expense record
        else:
            # Update the old record with new details from the form
            expensed = tendie_expenses.updateExpense(
                oldExpense, request.form, session["user_id"])
            if not expensed:
                return apology("The expense was unable to be updated.")

            # Redirect to results page and render a summary of the updated expense
            return render_template("expensed.html", results=expensed)


@app.route("/budgets", methods=["GET", "POST"])
@login_required
def budgets():
    """Manage budgets"""

    # User reached route via GET
    if request.method == "GET":
        # Get the users income
        income = tendie_dashboard.getIncome(session["user_id"])

        # Get the users current budgets
        budgets = tendie_budgets.getBudgets(session["user_id"])

        # Get the users total budgeted amount
        budgeted = tendie_budgets.getTotalBudgeted(session["user_id"])

        return render_template("budgets.html", income=income, budgets=budgets, budgeted=budgeted, deletedBudgetName=None)

    # User reached route via POST
    else:
        # Get the name of the budget the user wants to delete
        budgetName = request.form.get("delete").strip()

        # Delete the budget
        deletedBudgetName = tendie_budgets.deleteBudget(
            budgetName, session["user_id"])

        # Render the budgets page with a success message, otherwise throw an error/apology
        if deletedBudgetName:
            # Get the users income, current budgets, and sum their budgeted amount unless they don't have any budgets (same steps as a GET for this route)
            income = tendie_dashboard.getIncome(session["user_id"])
            budgets = tendie_budgets.getBudgets(session["user_id"])
            budgeted = tendie_budgets.getTotalBudgeted(session["user_id"])

            return render_template("budgets.html", income=income, budgets=budgets, budgeted=budgeted, deletedBudgetName=deletedBudgetName)
        else:
            return apology("Uh oh! Your budget could not be deleted.")


@app.route("/createbudget", methods=["GET", "POST"])
@login_required
def createbudget():
    """Create a budget"""

    # User reached route via POST
    if request.method == "POST":
        # Get all of the budget info provided from the HTML form
        formData = list(request.form.items())

        # Generate data structure to hold budget info from form
        budgetDict = tendie_budgets.generateBudgetFromForm(formData)
        # Render error message if budget name or categories contained invalid data
        if "apology" in budgetDict:
            return apology(budget["apology"])
        else:
            # Add budget to DB for user
            budget = tendie_budgets.createBudget(
                budgetDict, session["user_id"])
            # Render error message if budget name is a duplicate of another budget the user has
            if "apology" in budget:
                return apology(budget["apology"])
            else:
                return render_template("budgetcreated.html", results=budget)
    else:
        # TODO need to make sure user has at least 1 spend category otherwise no selects will appear for
        # budgeting (need to design something here that works for every page e.g. addexpense). Initial idea is to not allow user to delete ALL categories, must have at least 1.

        # Get the users income
        income = tendie_dashboard.getIncome(session["user_id"])

        # Get the users current budgets
        budgets = tendie_budgets.getBudgets(session["user_id"])

        # Get the users total budgeted amount
        budgeted = tendie_budgets.getTotalBudgeted(session["user_id"])

        # Get the users spend categories
        categories = tendie_categories.getSpendCategories(session["user_id"])

        return render_template("createbudget.html", income=income, budgeted=budgeted, categories=categories)


@app.route("/updatebudget/<urlvar_budgetname>", methods=["GET", "POST"])
@login_required
def updatebudget(urlvar_budgetname):
    """Update a budget"""

    # User reached route via POST
    if request.method == "POST":
        # Get all of the budget info provided from the HTML form
        formData = list(request.form.items())

        # Generate data structure to hold budget info from form
        budgetDict = tendie_budgets.generateBudgetFromForm(formData)

        # Render error message if budget name or categories contained invalid data
        if "apology" in budgetDict:
            return apology(budget["apology"])
        else:
            # Update budget in the DB for user
            budget = tendie_budgets.updateBudget(
                urlvar_budgetname, budgetDict, session["user_id"])

            # Render error message if budget name is a duplicate of another budget the user has
            if "apology" in budget:
                return apology(budget["apology"])
            else:
                return render_template("budgetcreated.html", results=budget)

    # User reached route via GET
    else:
        # Get the budget details from the DB based on the budget name provided via URL. Throw an apology/error if budget can't be found.
        budgetID = tendie_budgets.getBudgetID(
            urlvar_budgetname, session["user_id"])
        if budgetID is None:
            return apology("'" + urlvar_budgetname + "' budget does not exist.")
        else:
            budget = tendie_budgets.getBudgetByID(budgetID, session["user_id"])

        # Get the users income
        income = tendie_dashboard.getIncome(session["user_id"])

        # Get the users total budgeted amount
        budgeted = tendie_budgets.getTotalBudgeted(session["user_id"])

        # Generate the full, updatable budget data structure (name, amount for budget w/ all categories and their budgeted amounts)
        budget = tendie_budgets.getUpdatableBudget(budget, session["user_id"])

        # Render the budget update page
        return render_template("updatebudget.html", income=income, budgeted=budgeted, budget=budget)


@app.route("/categories", methods=["GET", "POST"])
@login_required
def categories():
    """Manage spending categories"""

    # User reached route via POST
    if request.method == "POST":

        # Initialize user's actions
        userHasSelected_newCategory = False
        userHasSelected_renameCategory = False
        userHasSelected_deleteCategory = False

        # Initialize user alerts
        alert_newCategory = None
        alert_renameCategory = None
        alert_deleteCategory = None

        # Determine what action was selected by the user (button/form trick from: https://stackoverflow.com/questions/26217779/how-to-get-the-name-of-a-submitted-form-in-flask)
        if "btnCreateCategory" in request.form:
            userHasSelected_newCategory = True
        elif "btnRenameCategory" in request.form:
            userHasSelected_renameCategory = True
        elif "btnDeleteCategory" in request.form:
            userHasSelected_deleteCategory = True
        else:
            return apology("Doh! Spend Categories is drunk. Try again!")

        # Get new category details and create a new record in the DB
        if userHasSelected_newCategory:

            # Get the new name provided by user
            newCategoryName = request.form.get("createName").strip()

            # Check to see if the new name already exists in the database (None == does not exist)
            categoryID = tendie_categories.getCategoryID(newCategoryName)

            # Category exists in the database already
            if categoryID:

                # Make sure the user isn't trying to add a category they already have by passing in the users ID now (None == does not exists)
                existingID = tendie_categories.getCategoryID(
                    newCategoryName, session["user_id"])
                if (existingID):
                    return apology("You already have '" + newCategoryName + "' category")
                # Add the category to the users account
                else:
                    tendie_categories.addCategory_User(
                        categoryID, session["user_id"])

            # Category does not exist in the DB already - create a new category and then add it to the users account
            else:
                # Creates a new category in the DB
                newCategoryID = tendie_categories.addCategory_DB(
                    newCategoryName)

                # Adds the category to the users account
                tendie_categories.addCategory_User(
                    newCategoryID, session["user_id"])

            # Set the alert message for user
            alert_newCategory = newCategoryName

        # Get renamed category details and update records in the DB
        if userHasSelected_renameCategory:

            # Get the new/old names provided by user
            oldCategoryName = request.form.get("oldname").strip()
            newCategoryName = request.form.get("newname").strip()

            # Check to see if the *old* category actually exists in the database (None == does not exist)
            oldCategoryID = tendie_categories.getCategoryID(oldCategoryName)

            # Old category does not exists in the database, throw error
            if oldCategoryID is None:
                return apology("The category you're trying to rename doesn't exist")

            # Check to see if the *new* name already exists in the database (None == does not exist)
            newCategoryID = tendie_categories.getCategoryID(newCategoryName)

            # Category exists in the database already
            if newCategoryID:

                # Make sure the user isn't trying to rename to a category they already have by passing in the users ID now (None == does not exists)
                existingID = tendie_categories.getCategoryID(
                    newCategoryName, session["user_id"])
                if existingID:
                    return apology("You already have '" + newCategoryName + "' category")

                # Get the new category name from the DB (prevents string upper/lowercase inconsistencies that can result from using the users input from the form instead of the DB)
                newCategoryNameFromDB = tendie_categories.getSpendCategoryName(
                    newCategoryID)

                # Rename the category
                tendie_categories.renameCategory(
                    oldCategoryID, newCategoryID, oldCategoryName, newCategoryNameFromDB, session["user_id"])

            # Category does not exist in the DB already - create a new category and then add it to the users account
            else:
                # Creates a new category in the DB
                newCategoryID = tendie_categories.addCategory_DB(
                    newCategoryName)

                # Rename the category
                tendie_categories.renameCategory(
                    oldCategoryID, newCategoryID, oldCategoryName, newCategoryName, session["user_id"])

            # Set the alert message for user
            alert_renameCategory = [oldCategoryName, newCategoryName]

        # Get deleted category details and update records in the DB
        if userHasSelected_deleteCategory:

            # Get the name of the category the user wants to delete
            deleteName = request.form.get("delete").strip()

            # Check to see if the category actually exists in the database (None == does not exist)
            categoryID = tendie_categories.getCategoryID(deleteName)

            # Category does not exists in the database, throw error
            if categoryID is None:
                return apology("The category you're trying to delete doesn't exist")

            # Get budgets that are currently using the category they want to delete
            budgets = tendie_categories.getBudgetsFromSpendCategory(
                categoryID, session["user_id"])

            # Delete categories from the users budgets
            if budgets:
                tendie_categories.deleteSpendCategoriesInBudgets(
                    budgets, categoryID)

            # Delete the category from the users account
            # TODO what should happen when a user deletes a category, and a budget that was using it now has NO categories checked?
            tendie_categories.deleteCategory_User(
                categoryID, session["user_id"])

            # Set the alert message for user
            alert_deleteCategory = deleteName

        # Get the users spend categories
        categories = tendie_categories.getSpendCategories(session["user_id"])

        return render_template("categories.html", categories=categories, newCategory=alert_newCategory, renamedCategory=alert_renameCategory, deleteCategory=alert_deleteCategory)

    # User reached route via GET
    else:
        # Get the users spend categories
        categories = tendie_categories.getSpendCategories(session["user_id"])

        # Get the budgets associated with each spend category
        categoryBudgets = tendie_categories.getBudgetsSpendCategories(
            session["user_id"])

        # Generate a single data structure for storing all categories and their associated budgets
        categoriesWithBudgets = tendie_categories.generateSpendCategoriesWithBudgets(
            categories, categoryBudgets)

        return render_template("categories.html", categories=categoriesWithBudgets, newCategory=None, renamedCategory=None, deleteCategory=None)


# Handle errors by rendering apology
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
