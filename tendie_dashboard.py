import os
import calendar
import tendie_budgets

from flask import request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import convertSQLToDict
from datetime import datetime

# Create engine object to manage connections to DB, and scoped session to separate user interactions with DB
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


# Get and return the users total spend for the current calendar year
def getTotalSpend_Year(userID):
    results = db.execute(
        "SELECT SUM(amount) AS expenses_year FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = date_part('year', CURRENT_DATE)",
        {"usersID": userID}).fetchall()

    totalSpendYear = convertSQLToDict(results)

    return totalSpendYear[0]['expenses_year']


# Get and return the users total spend for the current month
def getTotalSpend_Month(userID):
    results = db.execute(
        "SELECT SUM(amount) AS expenses_month FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = date_part('year', CURRENT_DATE) AND date_part('month', date(expensedate)) = date_part('month', CURRENT_DATE)",
        {"usersID": userID}).fetchall()

    totalSpendMonth = convertSQLToDict(results)

    return totalSpendMonth[0]['expenses_month']


# Get and return the users total spend for the current week
def getTotalSpend_Week(userID):
    # Query note: Day 0 of a week == Sunday. This query grabs expenses between the *current* weeks Monday and Sunday.
    results = db.execute(
        "SELECT SUM(amount) AS expenses_week FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = date_part('year', CURRENT_DATE) AND date_part('week', date(expensedate)) = date_part('week', CURRENT_DATE)",
        {"usersID": userID}).fetchall()

    totalSpendWeek = convertSQLToDict(results)

    return totalSpendWeek[0]['expenses_week']


# Get and return the users last 5 expenses
def getLastFiveExpenses(userID):
    results = db.execute(
        "SELECT description, category, expenseDate, payer, amount FROM expenses WHERE user_id = :usersID ORDER BY id DESC LIMIT 5", {"usersID": userID}).fetchall()

    lastFiveExpenses = convertSQLToDict(results)

    if lastFiveExpenses:
        return lastFiveExpenses
    else:
        return None


# Get and return all budgets for the user
def getBudgets(userID, year=None):
    budgets = []
    budget = {"name": None, "amount": 0, "spent": 0, "remaining": 0}

    # Default to getting current years budgets
    if not year:
        year = datetime.now().year

    budgets_query = tendie_budgets.getBudgets(userID)
    # Build a budget dict to return
    if budgets_query and year in budgets_query:
        for record in budgets_query[year]:
            budgetID = record["id"]
            budget["name"] = record["name"]
            budget["amount"] = record["amount"]

            # Query the DB for the budgets total spent amount (calculated as the sum of expenses with categories that match the categories selected for the individual budget)
            results = db.execute(
                "SELECT SUM(amount) AS spent FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = :year AND category IN (SELECT categories.name FROM budgetcategories INNER JOIN categories on budgetcategories.category_id = categories.id WHERE budgetcategories.budgets_id = :budgetID)",
                {"usersID": userID, "year": year, "budgetID": budgetID}).fetchall()
            budget_TotalSpent = convertSQLToDict(results)

            if (budget_TotalSpent[0]["spent"] == None):
                budget["spent"] = 0
            else:
                budget["spent"] = budget_TotalSpent[0]["spent"]

            # Set the remaining amount to 0 if the user has spent more than they budgeted for so that the charts don't look crazy
            if (budget["spent"] > budget["amount"]):
                budget["remaining"] = 0
            else:
                budget["remaining"] = budget["amount"] - budget["spent"]

            # Add the budget to the list
            budgets.append(budget.copy())

        return budgets

    # Return None if no budget was found
    else:
        return None


# Gets the last four weeks start dates and end dates (e.g. '2020-04-13' and '2020-04-19')
def getLastFourWeekNames():
    # Query note: looks back 3 weeks from the current week and *thru* the current week to give a total of 4 weeks of start/end dates
    results = db.execute("SELECT date_trunc('week', CURRENT_DATE)::date AS startofweek, (date_trunc('week', CURRENT_DATE) + interval '6 day')::date AS endofweek UNION SELECT date_trunc('week', CURRENT_DATE - interval '1 week')::date AS startofweek, (date_trunc('week', CURRENT_DATE - interval '1 week') + interval '6 day')::date AS endofweek UNION SELECT date_trunc('week', CURRENT_DATE - interval '2 week')::date AS startofweek, (date_trunc('week', CURRENT_DATE - interval '2 week') + interval '6 day')::date AS endofweek UNION SELECT date_trunc('week', CURRENT_DATE - interval '3 week')::date AS startofweek, (date_trunc('week', CURRENT_DATE - interval '3 week') + interval '6 day')::date AS endofweek ORDER BY startofweek ASC").fetchall()

    weekNames = convertSQLToDict(results)

    return weekNames


# Get and return weekly spending for the user (line chart)
def getWeeklySpending(weekNames, userID):
    weeklySpending = []
    week = {"startOfWeek": None, "endOfWeek": None, "amount": None}

    # Loop through each week and store the name/amount in a dict
    for name in weekNames:
        week["endOfWeek"] = name['endofweek'].strftime('%b %d')
        week["startOfWeek"] = name['startofweek'].strftime('%b %d')
        results = db.execute(
            "SELECT SUM(amount) AS amount FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = date_part('year', date(:weekName)) AND date_part('week', date(expensedate)) = date_part('week',date(:weekName))",
            {"usersID": userID, "weekName": str(name["endofweek"])}).fetchall()
        weekSpending = convertSQLToDict(results)

        # Set the amount to 0 if there are no expenses for a given week
        if weekSpending[0]["amount"] == None:
            week["amount"] = 0
        else:
            week["amount"] = weekSpending[0]["amount"]

        # Add the week to the list
        weeklySpending.append(week.copy())

    # Check to make sure at least 1 of the 4 weeks has expenses, otherwise set it to None so that the UI can be rendered with an appropriate message
    hasExpenses = False
    for record in weeklySpending:
        if record["amount"] != 0:
            hasExpenses = True
            break
    if hasExpenses is False:
        weeklySpending.clear()

    return weeklySpending


# Get and return monthly spending for a given year (bar chart)
def getMonthlySpending(userID, year=None):
    spending_month = []
    month = {"name": None, "amount": None}

    # Default to getting current years spending
    if not year:
        year = datetime.now().year

    results = db.execute(
        "SELECT date_part('month', date(expensedate)) AS month, SUM(amount) AS amount FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = :year GROUP BY date_part('month', date(expensedate)) ORDER BY month",
        {"usersID": userID, "year": year}).fetchall()
    spending_month_query = convertSQLToDict(results)

    for record in spending_month_query:
        month["name"] = calendar.month_abbr[int(record["month"])]
        month["amount"] = record["amount"]

        spending_month.append(month.copy())

    return spending_month


# Get and return trends for every spending category that accounts for >1% of overall spend (bubble chart)
def getSpendingTrends(userID, year=None):

    spending_trends = []
    categoryTrend = {"name": None, "proportionalAmount": None,
                     "totalSpent": None, "totalCount": None}

    # Default to getting current years spending
    if not year:
        year = datetime.now().year

    results = db.execute("SELECT category, COUNT(category) as count, SUM(amount) as amount FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = :year GROUP BY category ORDER BY COUNT(category) DESC",
                         {"usersID": userID, "year": year}).fetchall()
    categories = convertSQLToDict(results)

    # Calculate the total amount spent
    totalSpent = 0
    for categoryExpense in categories:
        totalSpent += categoryExpense["amount"]

    for category in categories:
        # Do not include category in chart if it's spending accounts for less than 1% of the overall spending
        proportionalAmount = round((category["amount"] / totalSpent) * 100)
        if (proportionalAmount < 1):
            continue
        else:
            categoryTrend["name"] = category["category"]
            categoryTrend["proportionalAmount"] = proportionalAmount
            categoryTrend["totalSpent"] = category["amount"]
            categoryTrend["totalCount"] = category["count"]
            spending_trends.append(categoryTrend.copy())

    return spending_trends
