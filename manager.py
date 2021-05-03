import database
import models
import reports
import helpers
from datetime import date

def hireNewStaffMember(db):
    print("==========")
    print("Hire new staff member:")
    print("* Note that the new staff member will be hired at the current active store.")
    print("==========")

    staffMember = models.Staff()

    # Prompt for name
    while True:
        staffMember.name = input("Name: ")
        if len(staffMember.name.strip()) == 0:
            print("Invalid input.  Try again.")
        else:
            break

    # Prompt for age
    while True:
        try:
            staffMember.age = int(input("Age: "))
            break
        except ValueError:
            print("Invalid input.  Try again.")

    # Prompt for address
    while True:
        staffMember.address = input("Address: ")
        if len(staffMember.address.strip()) == 0:
            print("Invalid input.  Try again.")
        else:
            break

    # Prompt for email
    while True:
        staffMember.email = input("Email: ")
        if len(staffMember.email.strip()) == 0:
            print("Invalid input.  Try again.")
        else:
            break

    # Prompt for phone
    while True:
        staffMember.phone = input("Phone: ")
        if len(staffMember.phone.strip()) == 0:
            print("Invalid input.  Try again.")
        else:
            break

    # Start date
    staffMember.startDt = date.today()

    # Prompt for department
    while True:
        staffMember.department = input("Department (Registration, Billing, Cashier, Warehouse, Manager): ")
        if len(staffMember.department.strip()) == 0 or staffMember.department.strip() not in ["Registration", "Billing", "Cashier", "Warehouse", "Manager"]:
            print("Invalid input.  Try again.")
        else:
            break
    
    # Prompt for title
    while True:
        staffMember.title = input("Title: ")
        if len(staffMember.title.strip()) == 0:
            print("Invalid input.  Try again.")
        else:
            break

    # Prompt for store
    reports.getAllStores(db)
    while True:
        try:
            storeId = int(input("Select a store for this staff member to work at (Store ID): "))
            store = database.validateStoreId(db, storeId)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    database.hireNewStaffMember(db, staffMember, store)
    print("New staffmember successfully hired.")

def updateStaffInfo(db):
    print("==========")
    print("Update staff member info:")
    print("==========")

    # Prompt for staff ID
    reports.getAllStaff(db)
    while True:
        try:
            staffId = int(input("Select a staff member to update (Staff ID): "))
            staffMember = database.validateStaffId(db, staffId)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    # Prompt for name
    newStaffMemberName = input(f"Enter a new name ({staffMember.name}): ")
    if len(newStaffMemberName.strip()) != 0:
        staffMember.name = newStaffMemberName

    # Prompt for age
    while True:
        try:
            newStaffMemberAge = input(f"Enter a new age ({staffMember.age}): ")
            if len(newStaffMemberAge.strip()) == 0:
                break
            staffMember.age = int(newStaffMemberAge)
            break
        except ValueError:
            print("Invalid input.  Try again.")

    # Prompt for address
    newStaffMemberAddress = input(f"Enter a new address ({staffMember.address}): ")
    if len(newStaffMemberAddress.strip()) != 0:
        staffMember.address = newStaffMemberAddress

    # Prompt for email
    newStaffMemberEmail = input(f"Enter a new email ({staffMember.email}): ")
    if len(newStaffMemberEmail.strip()) != 0:
        staffMember.email = newStaffMemberEmail

    # Prompt for phone
    newStaffMemberPhone = input(f"Enter a new phone ({helpers.getFormattedPhoneNumber(staffMember.phone)}): ")
    if len(newStaffMemberPhone.strip()) != 0:
        staffMember.phone = newStaffMemberPhone

    # Prompt for department
    newDepartment = input(f"Enter a new department ({staffMember.department}) (Choose from Registration, Billing, Cashier, Warehouse, Manager): ")
    newDepartment = newDepartment.strip()

    # Prompt for title
    newTitle = input(f"Enter a new title ({staffMember.title}): ")
    if len(newTitle.strip()) != 0:
        staffMember.title = newTitle

    # Prompt for store
    currentStoreForEmployee = database.getStoreForEmployee(db, staffMember.id)
    reports.getAllStores(db)
    while True:
        try:
            newStoreId = input(f"Enter a new store ({currentStoreForEmployee}): ")
            if len(newStoreId.strip()) == 0:
                break
            storeId = int(newStoreId)
            store = database.validateStoreId(db, storeId)
            currentStoreForEmployee = store.id
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    database.updateStaffInfo(db, staffMember, newDepartment, currentStoreForEmployee)
    print("Staff member information successfully updated.")

def fireStaffMember(db):
    print("==========")
    print("Fire staff member:")
    print("==========")

    # Prompt for staff ID
    reports.getAllStaff(db)
    while True:
        try:
            staffId = int(input("Select a staff member to fire (Staff ID): "))
            staffMember = database.validateStaffId(db, staffId)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    database.fireStaffMember(db, staffMember)
    print("Staff member successfully fired :(")

def updateStore(db):
    print("==========")
    print("Update store information:")
    print("==========")

    reports.getAllStores(db)

    # Prompt for store ID to update
    while True:
        try:
            storeId = int(input("Choose store to update (Store ID): "))
            storeToUpdate = database.validateStoreId(db, storeId)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    newAddress = input(f"Enter a new address ({storeToUpdate.address}): ")
    if len(newAddress.strip()) != 0:
        storeToUpdate.address = newAddress
    
    newPhone = input(f"Enter a new phone number ({helpers.getFormattedPhoneNumber(storeToUpdate.phone)}): ")
    if len(newPhone.strip()) != 0:
        storeToUpdate.phone = newPhone

    reports.getAllStaff(db, storeIds = [storeId])
    
    # Prompt for new general manager
    while True:
        try:
            newManagerId = input(f"Select a new manager by ID ({storeToUpdate.manager.id}): ")
            if len(newManagerId.strip()) == 0:
                break
            newManagerId = int(newManagerId)
            storeToUpdate.manager = database.validateStaffId(db, newManagerId)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    database.updateStoreInfo(db, storeToUpdate)
    print("Store successfully updated.")

def closeStore(db):
    print("==========")
    print("Close a store:")
    print("==========")

    reports.getAllStores(db)

    # Prompt for store ID to close
    while True:
        try:
            storeToClose = int(input("Choose store to close (Store ID): "))
            store = database.validateStoreId(db, storeToClose)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    database.closeStore(db, store)
    print("The store has been successfully closed.")

def openNewStore(db):
    print("==========")
    print("Open a new store:")
    print("==========")

    store = models.Store()

    # Prompt for address
    while True:
        store.address = input("Address: ")
        if len(store.address) == 0:
            print("Invalid input.  Try again.")
        else:
            break

    # Prompt for phone number
    while True:
        store.phone = input("Phone Number: ")
        if len(store.phone) == 0:
            print("Invalid input.  Try again.")
        else:
            break

    # Choose a store manager
    reports.getAllStaff(db)
    while True:
        try:
            manager = int(input("Select employee to manage store (Staff ID): "))
            store.manager = database.validateStaffId(db, manager)
            break
        except (ValueError, LookupError):
            print('Invalid Input.  Try again.')


    database.openNewStore(db, store)
    print("Successfully opened new store.")