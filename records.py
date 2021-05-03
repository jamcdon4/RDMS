import database
import models
import reports
from datetime import datetime
from database import DatabaseManager
from terminaltables import AsciiTable

########################################
### Billing and Transactions Records ###
########################################

# Create or generate bills that are to be paid to a specific supplier
def generateBillForSupplier(db):

    reports.getAllSuppliers(db)

    print("==========")
    print(" Generate bill for supplier: ")
    print("==========")

    reports.getAllSuppliers(db)

    supplier = models.Supplier()
    supplier.id = input("Supplier ID: ")

    bill = database.generateBillForSupplier(db, supplier)

    if (bill is not None):
        tableData = [['Supplier ID', 'Billing Amount']]
        td =[supplier.id, bill]
        tableData.append(td)
        table = AsciiTable(tableData)
        print(table.table)

# Generate reward checks for platinum customers that are due at the end of the year 
def generateRewardChecks(db):


    print("==========")
    print(" Generate reward check for platinum member: ")
    print("==========")

    reports.getAllCustomers(db)
    
    customer = models.Customer()
    reward = models.Reward()
    customer.id = int(input("Enter Customer ID: "))
    print("Current reward year: " + str(datetime.now().year))
    reward.year = datetime.now().year

    check = database.generateRewardChecks(db, customer, reward)

    if (check is not None):
        tableData = [['Customer ID', 'Reward Amount']]
        td =[customer.id, check]
        tableData.append(td)
        table = AsciiTable(tableData)
        print(table.table)