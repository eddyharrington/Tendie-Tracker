import os
import calendar
import copy
import tendie_expenses
import tendie_dashboard
import tendie_categories
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


# Generates data needed for the budget report by looping through each budget and adding expense history where categories match between budgets and expenses
# TODO: This data/reporting becomes less beneficial when users have multiple budgets that have the same categories checked because 1 expense with 'Category A' will be associated with for example 3 budgets that have 'Category A' checked
def generateBudgetsReport(userID, year=None):
    # Create data structure to hold users category spending data
    budgetsReport = []

    # Default to getting current years budgets
    if not year:
        year = datetime.now().year

    # Get every budgets spent/remaining for the user
    budgetsReport = tendie_dashboard.getBudgets(userID, year)

    # Loop through the budgets and add a new key/value pair to hold expense details per budget
    if budgetsReport:
        for record in budgetsReport:
            budgetID = tendie_budgets.getBudgetID(record["name"], userID)
            results = db.execute("SELECT expenses.description, expenses.category, expenses.expenseDate, expenses.payer, expenses.amount FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = :year AND category IN (SELECT categories.name FROM budgetcategories INNER JOIN categories on budgetcategories.category_id = categories.id WHERE budgetcategories.budgets_id = :budgetID)",
                                 {"usersID": userID, "year": year, "budgetID": budgetID}).fetchall()
            expenseDetails = convertSQLToDict(results)
            record["expenses"] = expenseDetails

    return budgetsReport


# Generates data needed for the monthly spending report
def generateMonthlyReport(userID, year=None):

    # Default to getting current years reports
    if not year:
        year = datetime.now().year

    # Create data structure to hold users monthly spending data for the chart (monthly summed data)
    spending_month_chart = tendie_dashboard.getMonthlySpending(userID, year)

    # Get the spending data from DB for the table (individual expenses per month)
    results = db.execute(
        "SELECT description, category, expensedate, amount, payer FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = :year ORDER BY id ASC", {"usersID": userID, "year": year}).fetchall()
    spending_month_table = convertSQLToDict(results)

    # Combine both data points (chart and table) into a single data structure
    monthlyReport = {"chart": spending_month_chart,
                     "table": spending_month_table}

    return monthlyReport


# Generates data needed for the spending trends report
def generateSpendingTrendsReport(userID, year=None):

    # Default to getting current years reports
    if not year:
        year = datetime.now().year

    # Get chart data for spending trends
    spending_trends_chart = tendie_dashboard.getSpendingTrends(userID, year)

    # Data structure for spending trends table
    categories = []
    category = {"name": None, "expenseMonth": 0,
                "expenseCount": 0, "amount": 0}
    spending_trends_table = {
        "January": [],
        "February": [],
        "March": [],
        "April": [],
        "May": [],
        "June": [],
        "July": [],
        "August": [],
        "September": [],
        "October": [],
        "November": [],
        "December": []
    }

    # Get all of the users categories first (doesn't include old categories the user deleted but are still tracked in Expenses)
    categories_active = tendie_categories.getSpendCategories(userID)

    # Get any categories that are in expenses but no longer exist as a selectable category for the user (because they deleted the category)
    categories_inactive = tendie_categories.getSpendCategories_Inactive(userID)

    # First fill using the users current categories, and then inactive categories from Expenses
    for activeCategory in categories_active:
        category["name"] = activeCategory["name"]
        categories.append(category.copy())

    for inactiveCategory in categories_inactive:
        category["name"] = inactiveCategory["category"]
        categories.append(category.copy())

    # Place a deep copy of the categories into each month (need deep copy here because every category may have unique spend data month to month. TODO: optimize this for memory/performance later)
    for month in spending_trends_table.keys():
        spending_trends_table[month] = copy.deepcopy(categories)

    # Get expense data for each category by month (retrieves the total amount of expenses per category by month, and the total count of expenses per category by month. Assumes there is at least 1 expense for the category)
    results = db.execute(
        "SELECT date_part('month', date(expensedate)) AS monthofcategoryexpense, category AS name, COUNT(category) AS count, SUM(amount) AS amount FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = :year GROUP BY date_part('month', date(expensedate)), category ORDER BY COUNT(category) DESC",
        {"usersID": userID, "year": year}).fetchall()

    spending_trends_table_query = convertSQLToDict(results)

    # Loop thru each monthly category expense from above DB query and update the data structure that holds all monthly category expenses
    for categoryExpense in spending_trends_table_query:
        # Get the key (month) for the data structure
        monthOfExpense = calendar.month_name[int(
            categoryExpense["monthofcategoryexpense"])]
        # Traverse the data structure: 1) go to the dict month based on the category expense date, 2) loop thru each dict category until a match in name occurs with the expense, 3) update the dict month/amount/count properties to match the DB record
        for category in spending_trends_table[monthOfExpense]:
            if category["name"] == categoryExpense["name"]:
                category["expenseMonth"] = categoryExpense["monthofcategoryexpense"]
                category["expenseCount"] = categoryExpense["count"]
                category["amount"] = categoryExpense["amount"]
                break
            else:
                continue

    # Calculates and stores the amount spent per category for the table (note: can't get this to work in jinja with the spending_trends_table dict because of how jinja scopes variables. TODO: rethink data-structure to combine these)
    numberOfCategories = len(categories)
    categoryTotal = 0
    # Loops through every month per category and sums up the monthly amounts
    for i in range(numberOfCategories):
        for month in spending_trends_table.keys():
            categoryTotal += spending_trends_table[month][i]["amount"]
        categories[i]["amount"] = categoryTotal
        categoryTotal = 0

    # Combine both data points (chart, table, categories) into a single data structure
    spendingTrendsReport = {"chart": spending_trends_chart,
                            "table": spending_trends_table, "categories": categories}

    return spendingTrendsReport


# Generates data needed for the payers spending report
def generatePayersReport(userID, year=None):

    # Default to getting current years reports
    if not year:
        year = datetime.now().year

    # First get all of the payers from expenses table (this may include payers that don't exist anymore for the user (i.e. deleted the payer and didn't update expense records))
    results_payers = db.execute(
        "SELECT payer AS name, SUM(amount) AS amount FROM expenses WHERE user_id = :usersID AND date_part('year', date(expensedate)) = :year GROUP BY payer ORDER BY amount DESC", {"usersID": userID, "year": year}).fetchall()
    payers = convertSQLToDict(results_payers)

    # Now get any payers the user has in their account but haven't expensed anything
    results_nonExpensePayers = db.execute(
        "SELECT name FROM payers WHERE user_id = :usersID AND name NOT IN (SELECT payer FROM expenses WHERE expenses.user_id = :usersID AND date_part('year', date(expensedate)) = :year)", {"usersID": userID, "year": year}).fetchall()
    nonExpensePayers = convertSQLToDict(results_nonExpensePayers)

    # Add the non-expense payers to the payers data structure and set their amounts to 0
    for payer in nonExpensePayers:
        newPayer = {"name": payer["name"], "amount": 0}
        payers.append(newPayer)

    # Calculate the total paid for all payers combined
    totalPaid = 0
    for payer in payers:
        totalPaid = totalPaid + payer["amount"]

    # Calculate the % paid per payer and add to the data structure
    if totalPaid != 0:
        for payer in payers:
            payer["percentAmount"] = round((payer["amount"] / totalPaid) * 100)

        return payers
    else:
        return None
