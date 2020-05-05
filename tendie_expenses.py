import calendar

from cs50 import SQL
from flask import request, session
from flask_session import Session
from datetime import datetime

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///budget.db")


# Add expense(s) to the users expense records
# There are two entry points for this: 1) 'addexpenses' route and 2) 'index' route. #1 allows many expenses whereas #2 only allows 1 expense per POST.
def addExpenses(formData, userID):
    expenses = []
    expense = {"description": None, "category": None,
               "date": None, "amount": None, "payer": None}

    # Check if the user is submitting via 'addexpenses' or 'index' route - this determines if a user is adding 1 or potentially many expenses in a single POST
    if "." not in formData[0][0]:
        for key, value in formData:
            # Add to dictionary
            expense[key] = value

        # Convert the amount from string to float for the DB
        expense["amount"] = float(expense["amount"])

        # Add dictionary to list
        expenses.append(expense.copy())
    else:
        counter = 0
        for key, value in formData:
            # Keys are numbered by default in HTML form. Remove those numbers so we can use the HTML element names as keys for the dictionary.
            cleanKey = key.split(".")

            # Add to dictionary
            expense[cleanKey[0]] = value

            # Every 5 loops add the expense to the list of expenses (because there are 5 fields for an expense record)
            counter += 1
            if counter % 5 == 0:
                # Store the amount as a float
                expense["amount"] = float(expense["amount"])

                # Add dictionary to list
                expenses.append(expense.copy())

    # Insert expenses into DB
    for expense in expenses:
        now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        db.execute("INSERT INTO expenses (description, category, expenseDate, amount, payer, submitTime, user_id) VALUES (:description, :category, :expenseDate, :amount, :payer, :submitTime, :usersID)",
                   description=expense["description"], category=expense["category"], expenseDate=expense["date"], amount=expense["amount"], payer=expense["payer"], submitTime=now, usersID=userID)

    return expenses
