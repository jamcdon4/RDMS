import database
import models
import reports
import helpers
from datetime import date
from database import DatabaseManager

def registerNewCustomer(db):
    print("==========")
    print("Register a new customer:")
    print("==========")

    # Prompt for Store ID
    reports.getAllStores(db)
    while True:
        try:
            storeId = int(input("Select a store to register customer at (Store ID): "))
            store = database.validateStoreId(db, storeId)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    # Prompt for Staff ID
    reports.getAllStaff(db, storeIds = [storeId])
    while True:
        try:
            staffId = int(input("Select a staff member who is registering the customer (Staff ID): "))
            staffMember = database.validateStaffId(db, staffId)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    customer = models.Customer()

    # Prompt for first name
    while True:
        customer.firstname = input("First Name: ")
        if len(customer.firstname.strip()) == 0:
            print("Invalid input.  Try again.")
        else:
            break

    # Prompt for last name
    while True:
        customer.lastname = input("Last Name: ")
        if len(customer.lastname.strip()) == 0:
            print("Invalid input.  Try again.")
        else:
            break

    # Prompt for email
    while True:
        customer.email = input("Email: ")
        if len(customer.email) == 0:
            print("Invalid input.  Try again.")
        else:
            break
    
    # Prompt for phone
    while True:
        customer.phone = input("Phone: ")
        if len(customer.phone) == 0:
            print("Invalid input.  Try again.")
        else:
            break

    # Prompt for address
    while True:
        customer.address = input("Address: ")
        if len(customer.address) == 0:
            print("Invalid input.  Try again.")
        else:
            break
    
    membership = models.Membership()

    # Prompt for membership level
    while True:
        membershipLevel = input("Membership Level (Bronze, Silver, Gold, Platinum): ")
        if len(membershipLevel) == 0 or membershipLevel not in ["Bronze", "Silver", "Gold", "Platinum"]:
            print("Invalid input.  Try again.")
        else:
            membership.level = models.MembershipLevel()
            membership.level.name = membershipLevel
            break

    # Prompt for membership length:
    while True:
        try:
            membership.length = int(input("Membership Length (Days): "))
            break
        except ValueError:
            print("Invalid input.  Try again.")

    membership.signUpDt = date.today()
    customer.membership = membership
    database.registerNewCustomer(db, customer, storeId, staffId)
    print("Customer successfully registered.")

def updateCustomerInformation(db):
    print("==========")
    print("Update a customer's information:")
    print("==========")

    reports.getAllCustomers(db)

    while True:
        try:
            customerId = int(input("Select a customer to update (Customer ID):"))
            customer = database.validateCustomerId(db, customerId)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    newFirstName = input(f"Enter a new first name ({customer.firstname}): ")
    if len(newFirstName.strip()) != 0:
        customer.firstname = newFirstName

    newLastName = input(f"Enter a new last name ({customer.lastname}): ")
    if len(newLastName.strip()) != 0:
        customer.lastname = newLastName

    newAddress = input(f"Enter a new address ({customer.address}): ")
    if len(newAddress.strip()) != 0:
        customer.address = newAddress

    newEmail = input(f"Enter a new email ({customer.email}): ")
    if len(newEmail.strip()) != 0:
        customer.email = newEmail

    newPhone = input(f"Enter a new phone ({helpers.getFormattedPhoneNumber(customer.phone)}): ")
    if len(newPhone.strip()) != 0:
        customer.phone = newPhone

    database.updateCustomerInfo(db, customer)
    print("Customer successfully updated.")
    
def unregisterCustomer(db):
    print("==========")
    print("Unregister a customer:")
    print("==========")

    reports.getAllCustomers(db)

    while True:
        try:
            customerId = int(input("Select a customer to update (Customer ID): "))
            customer = database.validateCustomerId(db, customerId)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    database.unregisterCustomer(db, customer)
    print("Customer successfully unregistered.")

def cancelMembership(db):
    print("==========")
    print("Cancel a customer's membership:")
    print("==========")

    reports.getAllCustomers(db)

    while True:
        try:
            customerId = int(input("Select a customer to update (Customer ID): "))
            customer = database.validateCustomerId(db, customerId)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    if not customer.membership.status:
        print(f"{customer.firstname} {customer.lastname}'s membership is already inactive.")
        print("This membership cannot be cancelled.")
        return
    
    while True:
        confirmation = input("Are you sure you wish to cancel this customer's membership? (y/n): ")
        if confirmation.strip() != 'y' or confirmation.strip() != 'y':
            print("Invalid input.  Try again.")
        else:
            break

    customer.membership.status = False
    database.updateMembership(db, customer)
    print("Membership successfully cancelled.")

def renewMembership(db):
    print("==========")
    print("Renew a customer's membership:")
    print("==========")

    reports.getAllCustomers(db)

    while True:
        try:
            customerId = int(input("Select a customer to update (Customer ID): "))
            customer = database.validateCustomerId(db, customerId)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    if not customer.membership.status:
        customer.membership.signUpDt = date.today()
        customer.membership.length = 0
    
    while True:
        try:
            length = int(input("Enter renewal length (days): "))
            if length <= 0:
                print("Invalid input.  Try again.")
            else:
                break
        except ValueError:
            print("Invalid input.  Try again.")
    
    customer.membership.length = customer.membership.length + length

    while True:
        membershipLevel = input(f"New membership level ({customer.membership.level.name}): ")
        if len(membershipLevel.strip()) != 0:
            if membershipLevel not in ["Bronze", "Silver", "Gold", "Platinum"]:
                print("Invalid input.  Try again.")
                continue
            customer.membership.level.name = membershipLevel
        break

    database.updateMembership(db, customer)
    print("Membership renewed successfully.")
    