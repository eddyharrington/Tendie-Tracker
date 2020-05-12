import calendar
import tendie_budgets

from cs50 import SQL
from flask import request, session
from flask_session import Session

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///budget.db")


# Get and return the users total spend for the current calendar year
def getTotalSpend_Year(userID):
    totalSpendYear = db.execute(
        "SELECT SUM(amount) AS 'expenses_year' FROM expenses WHERE user_id = :usersID AND expenseDate >= date('now','start of year') AND expenseDate < date('now','start of year','+1 year')",
        usersID=userID)

    return totalSpendYear[0]['expenses_year']


# Get and return the users total spend for the current month
def getTotalSpend_Month(userID):
    totalSpendMonth = db.execute(
        "SELECT SUM(amount) AS 'expenses_month' FROM expenses WHERE user_id = :usersID AND expenseDate < date('now','start of month','+1 month') AND expenseDate >= date('now','start of month')",
        usersID=userID)

    return totalSpendMonth[0]['expenses_month']


# Get and return the users total spend for the current week
def getTotalSpend_Week(userID):
    # Query note: Day 0 of a week == Sunday. This query grabs expenses between the *current* weeks Monday and Sunday.
    totalSpendWeek = db.execute(
        "SELECT SUM(amount) AS 'expenses_week' FROM expenses WHERE user_id = :usersID AND expenseDate <= date('now','weekday 0') AND expenseDate >= date('now','weekday 0','-6 day')",
        usersID=userID)

    return totalSpendWeek[0]['expenses_week']


# Get and return the users last 5 expenses
def getLastFiveExpenses(userID):
    lastFiveExpenses = db.execute(
        "SELECT description, category, expenseDate, payer, amount FROM expenses WHERE user_id = :usersID ORDER BY submitTime DESC LIMIT 5", usersID=userID)

    if lastFiveExpenses:
        return lastFiveExpenses
    else:
        return None


# Get and return all budgets for the user
def getBudgets(userID):
    budgets = []
    budget = {"id": None, "name": None,
              "amount": 0, "spent": 0, "remaining": 0}

    budgets_query = tendie_budgets.getBudgets(userID)
    # Build a budget dict to return
    if budgets_query:
        for record in budgets_query:
            budget["id"] = record["id"]
            budget["name"] = record["name"]
            budget["amount"] = record["amount"]

            # Query the DB for the budgets total spent amount (calculated as the sum of expenses with categories that match the categories selected for the individual budget)
            budget_TotalSpent = db.execute(
                "SELECT SUM(amount) AS 'spent' FROM expenses WHERE user_id = :usersID AND strftime('%Y',expenseDate) >= strftime('%Y','now') AND strftime('%Y',expenseDate) < strftime('%Y','now','+1 year') AND category IN (SELECT categories.name FROM budgetCategories INNER JOIN categories on budgetCategories.category_id = categories.id WHERE budgetCategories.budgets_id = :budgetID)",
                usersID=userID, budgetID=budget["id"])
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
    weekNames = db.execute("select date('now','weekday 0','-6 day') AS 'startOfWeek', date('now','weekday 0') AS 'endOfWeek' UNION select date('now','-7 day','weekday 0','-6 day') AS 'startOfWeek', date('now','-7 day','weekday 0') AS 'endOfWeek' UNION select date('now','-14 day','weekday 0','-6 day') AS 'startOfWeek', date('now','-14 day','weekday 0') AS 'endOfWeek' UNION select date('now','-21 day','weekday 0','-6 day') AS 'startOfWeek', date('now','-21 day','weekday 0') AS 'endOfWeek'")

    return weekNames


# Get and return weekly spending for the user (line chart)
def getWeeklySpending(weekNames, userID):
    weeklySpending = []
    week = {"startOfWeek": None, "endOfWeek": None, "amount": None}

    # Loop through each week and store the name/amount in a dict
    for name in weekNames:
        week["endOfWeek"] = name["endOfWeek"]
        week["startOfWeek"] = name["startOfWeek"]
        weekSpending = db.execute(
            "SELECT SUM(amount) AS 'amount' FROM expenses WHERE user_id = :usersID AND strftime('%W',expenseDate) = strftime('%W',:weekName)",
            usersID=userID, weekName=week["endOfWeek"])

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


# Get and return monthly spending for the user (bar chart)
def getMonthlySpending(userID):
    spending_month = []
    month = {"name": None, "amount": None}

    # Query note: pulls data for months of the *current* calendar year
    spending_month_query = db.execute(
        "SELECT LTRIM(strftime('%m',expenseDate),0) AS 'month', SUM(amount) AS 'amount' FROM expenses WHERE user_id = :usersID AND expenseDate > date('now','-11 month','start of month','-1 day') GROUP BY (strftime('%m',expenseDate))",
        usersID=userID)

    for record in spending_month_query:
        month["name"] = calendar.month_abbr[int(record["month"])]
        month["amount"] = record["amount"]

        spending_month.append(month.copy())

    return spending_month


# Get and return trends for every spending category that accounts for >1% of overall spend (bubble chart)
def getSpendingTrends(userID):
    spending_trends = []
    categoryTrend = {"name": None, "proportionalAmount": None,
                     "totalSpent": None, "totalCount": None}
    categories = db.execute("SELECT category, COUNT(category) as 'count', SUM(amount) as 'amount' FROM expenses WHERE user_id = :usersID GROUP BY category ORDER BY COUNT(category) DESC",
                            usersID=userID)

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
