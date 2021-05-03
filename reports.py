import database
import phonenumbers
import helpers
import datetime
from database import DatabaseManager
from terminaltables import AsciiTable
from datetime import timedelta

# Print a formatted table with all supplier information
def getAllSuppliers(db):
    suppliers = database.getSuppliers(db)
    tableData = [
        ['Supplier ID', 'Name', 'Address', 'Email', 'Phone', 'Num Shipments']
    ]

    for supplier in suppliers:
        supplierData = [
            supplier.id,
            supplier.name,
            supplier.location,
            supplier.email,
            helpers.getFormattedPhoneNumber(supplier.phone),
            len(supplier.shipments)
        ]
        tableData.append(supplierData)
    
    table = AsciiTable(tableData)
    print(table.table)

# Print a formatted table with all customer information
def getAllCustomers(db):
    customers = database.getCustomers(db)
    tableData = [
        ['Customer ID', 'First Name', 'Last Name', 'Address', 'Email', 'Phone', 'Membership Status', 'Membership Level', 'Membership Sign Up', 'Membership Expiration', 'Total Rewards']
    ]

    for customer in customers:
        customerData = [
            customer.id,
            customer.firstname, 
            customer.lastname, 
            customer.address, 
            customer.email, 
            helpers.getFormattedPhoneNumber(customer.phone), 
            "Active" if customer.membership.status == 1 else "Inactive", 
            customer.membership.level.name, 
            customer.membership.signUpDt, 
            customer.membership.signUpDt + timedelta(customer.membership.length),
            helpers.getFormattedPrice(sum([reward.amount for reward in customer.rewards]))
        ]
        tableData.append(customerData)

    table = AsciiTable(tableData)
    print(table.table)

# Print a formatted table with all store information
def getAllStores(db):
    stores = database.getStores(db)
    tableData = [
        ['Store ID', 'Address', 'Phone', 'Num Employees', 'Manager'] 
    ]
    for store in stores:
        storeData = [
            store.id,
            store.address,
            helpers.getFormattedPhoneNumber(store.phone), 
            len(store.staff),
            store.manager.name if store.manager is not None else ''
        ]
        tableData.append(storeData)

    table = AsciiTable(tableData)
    print(table.table)

# Print a formatted table with all staff information
def getAllStaff(db):
    staff = database.getStaff(db)
    tableData = [
        ['Staff ID', 'Name', 'Age', 'Title', 'Tenure', 'Email', 'Phone', 'Address', 'Department']
    ]
    for staffMember in staff:
        staffMemberData = [
            staffMember.id,
            staffMember.name,
            staffMember.age,
            staffMember.title,
            staffMember.startDt,
            staffMember.email,
            helpers.getFormattedPhoneNumber(staffMember.phone),
            staffMember.address,
            staffMember.department
        ]
        tableData.append(staffMemberData)

    table = AsciiTable(tableData)
    print(table.table)

# Print a formatted table with all product information
def getAllProducts(db, storeIds = None, supplierIds = None):
    products = database.getProducts(db, storeIds = storeIds, supplierIds = supplierIds)
    tableData = [
        ['Product ID', 'Store ID', 'Product', 'Quantity', 'Cost', 'Price', 'Sale Price', 'Sale Start', 'Sale End', 'Manufacture Date', 'Expiration Date', 'Supplier']
    ]

    for product in products:
        productData = [
            product.id[0],
            product.id[1],
            product.name,
            product.quantity,
            product.cost,
            helpers.getFormattedPrice(product.price),
            helpers.getFormattedPrice(product.salePrice),
            product.activeDiscount.startDt if product.activeDiscount is not None else "-",
            product.activeDiscount.endDt if product.activeDiscount is not None else "-",
            product.productionDt,
            product.expirationDt,
            product.supplier.name
        ]
        tableData.append(productData)
    
    table = AsciiTable(tableData)
    print(table.table)

# Print a formatted table with all staff information
def getAllStaff(db, storeIds = None):
    staff = database.getStaff(db, storeIds=storeIds)
    tableData = [
        ['Staff ID', 'Name', 'Age', 'Title', 'Tenure', 'Email', 'Phone', 'Address', 'Department']
    ]
    for staffMember in staff:
        staffMemberData = [
            staffMember.id,
            staffMember.name,
            staffMember.age,
            staffMember.title,
            staffMember.startDt,
            staffMember.email,
            helpers.getFormattedPhoneNumber(staffMember.phone),
            staffMember.address,
            staffMember.department
        ]
        tableData.append(staffMemberData)

    table = AsciiTable(tableData)
    print(table.table)

# Print a formatted table with all discount information
def getAllDiscounts(db):
    products = database.getProducts(db)
    discounts = {}
    for product in products:
        discounts[product.id] = []
        for discount in product.discounts:
            today = datetime.date.today()
            # Skip expired discounts
            if today > discount.endDt:
                continue
            discounts[product.id].append(discount)

    tableData = [
        ['Discount ID', 'Percent', 'Start Date', 'End Date', 'Product ID', 'Store ID']
    ]

    for productId, discountList in discounts.items():
        for discount in discountList:
            discountData = [
                discount.id,
                helpers.getFormattedDecimalAsPercent(discount.percent),
                discount.startDt,
                discount.endDt,
                productId[0],
                productId[1]
            ]
            tableData.append(discountData)

    table = AsciiTable(tableData)
    print(table.table)

# Print a formatted table with all sales information by date
def getSalesForDate(db):

    year = month = day = ""

    # Prompt for year
    while True:
        try:
            year = int(input("Enter date as YYYY: "))
            break
        except ValueError:
            print('Invalid Input.  Try again.')

    # Prompt for month (optional)
    while True:
        try:
            month = input("Enter month as MM (or press enter to skip): ")
            if month == "":
                break
            int(month)
            break
        except ValueError:
            print('Invalid Input.  Try again.')

    # Prompt for day (optional)
    if month != "":
        while True:
            try:
                day = input("Enter date as DD (or press enter to skip): ")
                if day == "":
                    break
                int(day)
                break
            except ValueError:
                print('Invalid Input.  Try again.')

    # Query for provided date
    totalSales = database.getSalesForDate(db, year, month, day)

    # Make Table
    tableData = [['Total Sales']]
    tableData.append([totalSales])

    table = AsciiTable(tableData)
    print(table.table)

# Print a formatted table with all sales information by store
def getSalesForStore(db):

    startDate = endDate = storeID = ""

    # Prompt for storeID
    getAllStores(db)
    while True:
        try:
            storeID = int(input("Enter a StoreID: "))
            break
        except ValueError:
            print('Invalid Input.  Try again.')

    # Prompt for startDate
    while True:
        try:
            startDate = input("Enter a start date as YYYY-MM-DD: ")
            datetime.datetime.strptime(startDate, '%Y-%m-%d')
            break
        except ValueError:
            print('Invalid Input.  Try again.')

    # Prompt for endDate
    while True:
        try:
            endDate = input("Enter an end date as YYYY-MM-DD: ")
            datetime.datetime.strptime(endDate, '%Y-%m-%d')
            break
        except ValueError:
            print('Invalid Input.  Try again.')

    # Query for provided store and date range
    totalSales = database.getSalesForStore(db, storeID, startDate, endDate)

    # Make Table
    tableData = [['Total Sales']]
    tableData.append([totalSales])

    table = AsciiTable(tableData)
    print(table.table)

# Print a formatted table with all stock information for store
def getStockForStore(db):

    storeID = ""

    getAllStores(db)
    # Prompt for storeID
    while True:
        try:
            storeID = int(input("Enter a StoreID: "))
            break
        except ValueError:
            print('Invalid Input.  Try again.')

    # Query for provided store and date range
    totalStock = database.getStockForStore(db, storeID)

    # Make Table
    tableData = [['Shipment Cost', 'Quantity', 'ShipID', 'ProductID', 'StoreID']]
    for stockItem in totalStock:
        staffMemberData = [
            stockItem.cost,
            stockItem.quantity,
            stockItem.shipID,
            stockItem.productID,
            stockItem.storeID
        ]
        tableData.append(staffMemberData)

    table = AsciiTable(tableData)
    print(table.table)

# Print a formatted table with all stock information product
def getStockForProduct(db):

    productID = ""

    getAllProducts(db)
    # Prompt for Product ID
    while True:
        try:
            storeID = int(input("Enter a productID: "))
            break
        except ValueError:
            print('Invalid Input.  Try again.')

    # Query for provided store and date range
    totalStock = database.getStockForProduct(db, storeID)

    # Make Table
    tableData = [['Shipment Cost', 'Quantity', 'ShipID', 'ProductID', 'StoreID']]
    for stockItem in totalStock:
        staffMemberData = [
            stockItem.cost,
            stockItem.quantity,
            stockItem.shipID,
            stockItem.productID,
            stockItem.storeID
        ]
        tableData.append(staffMemberData)

    table = AsciiTable(tableData)
    print(table.table)

# Print a formatted table with all customer information by date
def getCustomerForDate(db):

    year = month = ""

    # Prompt for year
    while True:
        try:
            year = int(input("Enter date as YYYY: "))
            break
        except ValueError:
            print('Invalid Input.  Try again.')

    # Prompt for month (optional)
    while True:
        try:
            month = input("Enter month as MM (or press enter to skip): ")
            if month == "":
                break
            int(month)
            break
        except ValueError:
            print('Invalid Input.  Try again.')

    # Query for provided store and date range
    totalCustomer = database.getCustomerForDate(db, year, month)

    # Make Table
    tableData = [['Total Customers']]
    tableData.append([totalCustomer])

    table = AsciiTable(tableData)
    print(table.table)

# Print a formatted table with all sale information by date
def getPurchasesForDate(db):

    startDate = endDate = custID = ""

    # Prompt for custID
    getAllCustomers(db)

    while True:
        try:
            custID = int(input("Enter a CustID: "))
            break
        except ValueError:
            print('Invalid Input.  Try again.')

    # Prompt for startDate
    while True:
        try:
            startDate = input("Enter a start date as YYYY-MM-DD: ")
            datetime.datetime.strptime(startDate, '%Y-%m-%d')
            break
        except ValueError:
            print('Invalid Input.  Try again.')

    # Prompt for endDate
    while True:
        try:
            endDate = input("Enter an end date as YYYY-MM-DD: ")
            datetime.datetime.strptime(endDate, '%Y-%m-%d')
            break
        except ValueError:
            print('Invalid Input.  Try again.')

    # Query for provided store and date range
    totalPurchases = database.getPurchasesForDate(db, startDate, endDate, custID)

    # Make Table
    tableData = [['Total Purchases']]
    tableData.append([totalPurchases])

    table = AsciiTable(tableData)
    print(table.table)

# Print a formatted table with all transaction information
def getAllTransactions(db):
    transactions = database.getTransactions(db)
    tableData = [
        ['Transaction ID', 'Date', 'Store', 'Customer', 'Cashier', 'Total Items', 'Total Value', 'Num Returned', 'Returned Value', 'Num Purchased', 'Purchased Value' ]
    ]

    for transaction in transactions:
        transactionData = [
            transaction.id,
            transaction.date,
            transaction.store.address if transaction.store is not None else "-",
            f"{transaction.customer.firstname} {transaction.customer.lastname}" if transaction.customer is not None else "-",
            transaction.staff.name if transaction.staff is not None else "-",
            sum([ti.quantity for ti in transaction.transactionProducts]),
            helpers.getFormattedPrice(sum([ti.pricePaid for ti in transaction.transactionProducts])),
            sum([ti.quantity for ti in transaction.transactionProducts if ti.status == False]),
            helpers.getFormattedPrice(sum([ti.pricePaid for ti in transaction.transactionProducts if ti.status == False])),
            sum([ti.quantity for ti in transaction.transactionProducts if ti.status == True]),
            helpers.getFormattedPrice(sum([ti.pricePaid for ti in transaction.transactionProducts if ti.status == True]))
        ]
        tableData.append(transactionData)

    table = AsciiTable(tableData)
    print(table.table)

# Print a formatted table with all transaction item information for transaction
def getAllTransactionItemsForTransaction(db, transaction):
    tableData = [
        ['Transaction Item ID', 'Product', 'Quantity', 'Status', 'Price', 'Total Price']
    ]

    counter = 1
    for transactionItem in transaction.transactionProducts:
        transactionItemData = [
            counter,
            transactionItem.product.name,
            transactionItem.quantity,
            "Purchased" if transactionItem.status else "Refunded",
            helpers.getFormattedPrice(transactionItem.price),
            helpers.getFormattedPrice(transactionItem.pricePaid)
        ]
        tableData.append(transactionItemData)
        counter = counter + 1

    table = AsciiTable(tableData)
    print(table.table)