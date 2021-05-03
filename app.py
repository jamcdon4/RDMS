import reports
import database
import registration
import manager
import billing
import cashier
import warehouse
import records
from database import DatabaseManager
import menu3

db = DatabaseManager()
db.initializeConnection()

m = menu3.Menu(True)

# List of operations supported in the menu
# Organized by operation
# Each has a function it executes, as well as a tuple of args it takes that is later unpacked
operations = {
    'Store Operations': {
        'View All Stores': {
            'func': reports.getAllStores,
            'args': (db,)
        },
        'Open a New Store': {
            'func': manager.openNewStore,
            'args': (db,)
        },
        'Update an Existing Store': {
            'func': manager.updateStore,
            'args': (db,)    
        },
        'Close a Store': {
            'func': manager.closeStore,
            'args': (db,)
        },
        'Return to Previous': None
    },
    'Staff Operations': {
        'View All Staff': {
            'func': reports.getAllStaff,
            'args': (db,)
        },
        'Hire a New Staff Member': {
            'func': manager.hireNewStaffMember,
            'args': (db,)
        },
        'Update Staff Member Information': {
            'func': manager.updateStaffInfo,
            'args': (db,)
        },
        'Fire a Staff Member': {
            'func': manager.fireStaffMember,
            'args': (db,)
        },
        'Return to Previous': None
    },
    'Customer Operations': {
        'View All Customers': {
            'func': reports.getAllCustomers,
            'args': (db,)
        },
        'Register a New Customer': {
            'func': registration.registerNewCustomer,
            'args': (db,)
        },
        'Update Customer Information': {
            'func': registration.updateCustomerInformation,
            'args': (db,)
        },
        'Unregister Customer': {
            'func': registration.unregisterCustomer,
            'args': (db,)
        },
        'Renew or Update Membership': {
            'func': registration.renewMembership,
            'args': (db,)
        },
        'Cancel Membership': {
            'func': registration.cancelMembership,
            'args': (db,)
        },
        'Return to Previous': None
    },
    'Supplier Operations': {
        'View All Suppliers': {
            'func': reports.getAllSuppliers,
            'args': (db,)
        },
        'Source a New Supplier': {
            'func': billing.sourceNewSupplier,
            'args': (db,)
        },
        'Update Supplier Information': {
            'func': billing.updateSupplierInfo,
            'args': (db,)
        },
        'Remove a Supplier': {
            'func': billing.removeSupplier,
            'args': (db,)
        },
        'Return to Previous': None
    },
    'Product Operations': {
        'View All Products': {
            'func': reports.getAllProducts,
            'args': (db,)
        },
        'Add a New Product': {
            'func': warehouse.addNewProduct,
            'args': (db,)
        },
        'Update Product Information' :{
            'func': warehouse.updateProductInformation,
            'args': (db,)
        },
        'Order Products': {
            'func': warehouse.orderProduct,
            'args': (db,)
        },
        'Transfer Products Between Stores': {
            'func': warehouse.transferProductsBetweenStores,
            'args': (db,)
        },
        'View All Discounts': {
            'func': reports.getAllDiscounts,
            'args': (db,)
        },
        'Add a Discount': {
            'func': billing.putProductOnSale,
            'args': (db,)
        },
        'Modify a Discount': {
            'func': billing.modifyDiscount,
            'args': (db,)
        },
        'Return to Previous': None
    },
    'Transactions': {
        'View All Transactions': {
            'func': reports.getAllTransactions,
            'args': (db,)
        },
        'Checkout Customer': {
            'func': cashier.checkoutCustomer,
            'args': (db,)
        },
        'Process Return': {
            'func': cashier.processReturn,
            'args': (db,)
        },
        'Return to Previous': None
    },
    'Billing Operations': {
        'Create or generate bills that are to be paid to a specific supplier.': {
            'func': records.generateBillForSupplier,
            'args': (db,)
        },
        'Generate reward checks for platinum customers that are due at the end of the year.': {
            'func': records.generateRewardChecks,
            'args': (db,)
        },
        'Return to Previous': None
    },
    'Reports': {
        'Generate total sales report by day, by month, or by year.': {
            'func': reports.getSalesForDate,
            'args': (db,)
        },
        'Sales growth report for a specific store for a given time period': {
            'func': reports.getSalesForStore,
            'args': (db,)
        },
        'Merchandise stock report for a certain store': {
            'func': reports.getStockForStore,
            'args': (db,)
        },
        'Merchandise stock report for a certain product': {
            'func': reports.getStockForProduct,
            'args': (db,)
        },
        'Customer growth report by month or by year': {
            'func': reports.getCustomerForDate,
            'args': (db,)
        },
        'Customer activity report such as total purchase amount for a given time period': {
            'func': reports.getPurchasesForDate,
            'args': (db,)
        },
        'Return to Previous': None
    },
    'Quit': None
}

# Handle the menu and the submenu
# Execute the command as needed
def printMenu():
    menu = [key for key in operations]
    c1 = m.menu("Please select from the following", menu, "Choice: ") - 1
    print(chr(27) + "[2J")
    print(menu[c1])
    
    if menu[c1] == 'Quit':
        return False

    subMenu = [key for key in operations[menu[c1]]]
    c2 = m.menu("Please select from the following", subMenu, "Choice: ") - 1
    print(subMenu[c2])

    currentOp = operations[menu[c1]][subMenu[c2]]
    if currentOp is None:
        return True

    func = operations[menu[c1]][subMenu[c2]]['func']
    args = operations[menu[c1]][subMenu[c2]]['args']
    func(*args)

    return True

print("============================================================")
print("Welcome to the WolfWR Management System")
print("============================================================")

while printMenu():
    pass

db.closeConnection()