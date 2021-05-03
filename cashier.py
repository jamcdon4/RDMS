import reports
import records
import database

def checkoutCustomer(db):
    reports.getAllStores(db)
    while True:
        try:
            storeID = int(input("Enter a StoreID: "))
            store = database.validateStoreId(db, storeID)
            break
        except (ValueError, LookupError):
            print('Invalid Input.  Try again.')

    # Prompt for staffID
    reports.getAllStaff(db, storeIds = [storeID])
    while True:
        try:
            staffID = int(input("Enter a StaffID: "))
            staff = database.validateStaffId(db, staffID)
            break
        except (ValueError, LookupError):
            print('Invalid Input.  Try again.')

    # Prompt for custID
    reports.getAllCustomers(db)
    while True:
        try:
            custID = int(input("Enter a CustID: "))
            customer = database.validateCustomerId(db, custID)
            break
        except (ValueError, LookupError):
            print('Invalid Input.  Try again.')

    database.addTransaction(db, custID, staffID, storeID)

    while True:
        reports.getAllProducts(db, storeIds = [storeID])
        while True:
            try:
                productID = input("Enter product ID (or press enter to quit transaction): ")
                if productID == "":
                    break
                product = database.validateProductId(db, int(productID), storeID)
                break
            except ValueError:
                print('Invalid Input.  Try again.')

        if productID != "":
            while True:
                try:
                    quantity = input("Enter quantity (or press enter to quit transaction): ")
                    if quantity == "":
                        break
                    quantity = int(quantity)
                    break
                except ValueError:
                    print('Invalid Input.  Try again.')

        if productID == '' or quantity == '':
            break
        else:
            database.addTransactionItem(db, product, store, quantity)
    print("Transaction successfully completed.")

def processReturn(db):
    # Prompt for transaction ID
    reports.getAllTransactions(db)
    while True:
        try:
            transactionID = int(input("Enter a transactionID: "))
            transaction = database.validateTransactionId(db, transactionID)
            break
        except (ValueError, LookupError):
            print('Invalid Input.  Try again.')

    while True:
        # Prompt for transactionItem to refund
        reports.getAllTransactionItemsForTransaction(db, transaction)
        while True:
            try:
                transItemId = input("Choose Transaction Item to refund (or press enter to quit refund) (Transaction Item ID): ")
                if transItemId == "":
                    break
                transItemId = int(transItemId)
                break
            except ValueError:
                print('Invalid Input.  Try again.')

        if transItemId == "":
            break
        else:
            transactionItem = transaction.transactionProducts[transItemId - 1]
            if transactionItem.status == False:
                print("Item is already refunded.  It cannot be refunded again.")
                continue
            transactionItem.status = False
            database.updateTransactionItem(db, transaction, transactionItem)
    
    print("Refund successfully processed.")
        