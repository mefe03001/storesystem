#!/bin/python

import mariadb
import datetime
from tabulate import tabulate

connection = mariadb.connect(
    user="sqluser",
    password="Passwd!#%",
    host="localhost",
    database="project"
)

cursor = connection.cursor()


def getcmdhelp():
    print("Help for the different commands:")
    print("exit: logout if logged in. If not logged in, exists the application.")
    print("cart")
    print("\tcart add [id] [amount]: add an item id to your cart")
    print("\tcart list: list all items in the cart")
    print("\tcart rm: clear the list")
    print("\tcart rm [id]: remove an item from the cart")
    print("\tcart rm [id] [amount]: remove a specified amount items from the cart")
    print("order\n")
    print("\torder send: send your order")
    print("\torder list: list all your orders")
    print("\torder list completed: list all your completed orders")
    print("\torder list completed: list all your uncompleted orders")
    print("\torder details [order_id]: see content of an order")
    print("store")
    print("\tstore all: list all items available in the store")
    print("\tstore list: list all filters")
    print("\tstore category: list all categories in the store")
    print("\tstore category [catecory name]: list all available under a specified category")
    print("\tstore manufacturer: list all manufacturers in the store")
    print("\tstore manufacturer [manufacturer name]: list all items from a specified manufacturers")

    
def cart(customer_id, inputparameters):
    if inputparameters[1] == "add":
        if len(inputparameters) == 4:
            cursor.execute("INSERT INTO cart (customer_id, item_id, amount) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE amount = amount + VALUES(amount)", (customer_id[0], inputparameters[2], inputparameters[3]))
            connection.commit()
            print(f"Added {inputparameters[3]} item_id {inputparameters[2]}")
        else:
            print("Error: cart list requires an item_id and an amount")

    elif inputparameters[1] == "list":
        cursor.execute("SELECT c.item_id, i.item_name, i.price, c.amount, (i.price * c.amount) AS total_cost FROM cart c JOIN items i ON c.item_id = i.item_id WHERE c.customer_id = %s", (customer_id[0],))
        print("You currently have following items in your cart:")
        headers = ("id", "name", "price", "amount", "total")
        data = [row for row in cursor.fetchall()]
        print(tabulate(data, headers=headers, tablefmt="grid"))
        print("The current total price of all items are: $", end="")
        cursor.execute("SELECT sum(i.price * c.amount) AS total_cost FROM cart c JOIN items i ON c.item_id = i.item_id WHERE c.customer_id = %s", (customer_id[0],))
        print(cursor.fetchone()[0])
    
    elif inputparameters[1] == "rm":
        if len(inputparameters) == 2:
            cursor.execute("DELETE FROM cart WHERE customer_id = %s", (customer_id[0],))
            connection.commit()
            print(f"Removed all items from your cart")
        elif len(inputparameters) == 3:
            cursor.execute("DELETE FROM cart WHERE customer_id = %s AND item_id = %s", (customer_id[0], inputparameters[2]))
            connection.commit()
            print(f"Removed item id {inputparameters[2]} from your cart")
        elif len(inputparameters) == 4:
            cursor.execute("UPDATE cart SET amount = amount - %s WHERE customer_id = %s AND item_id = %s", (inputparameters[3], customer_id[0], inputparameters[2]))
            connection.commit()
            print(f"Removed {inputparameters[3] }item id {inputparameters[2]} from your cart")
    else:
        print("Error: command not found. Use help to learn how to use the commands!")

def order(customer_id, inputparameters):
    if inputparameters[1] == "send":
        print("Are you sure you want to send the following order?")
        cart(customer_id, ["cart", "list"])

        unanswered = True
        while(unanswered):
            orderconfirmation = input("Answer yes or no: ")
            if orderconfirmation == "yes":
                unanswered = False
            elif orderconfirmation == "no":
                print("You answered 'no', returning to order interface.")
                return
            else:
                print("Answer yes or no!")
        
        cursor.execute("SELECT create_order(%s)", (customer_id[0],))
        connection.commit()
        result = cursor.fetchone()[0]
        
        if result == 1:
            print("Order was sucessful\nEnter 'order list' to view the status of your orders.")            
        elif result == 0:
            print("You order exceeded the available stock and was not able to be placed.")
        elif result == -1:
            print("You do not have anything in your cart. Place something in your cart to be able to create an order.")
    
    elif inputparameters[1] == "list":
        if len(inputparameters) == 2:
            headers = ["Order ID", "Time ordered", "Completed", "Total price"]
            cursor.execute("SELECT o.order_id, o.datetime_ordered, o.completed, sum(oi.quantity * i.price) AS total_cost FROM orders o JOIN ordered_items oi ON oi.order_id = o.order_id JOIN items i ON oi.item_id = i.item_id WHERE o.customer_id = %s GROUP BY o.order_id", (customer_id[0],))
            data = [row for row in cursor.fetchall()]
            print(tabulate(data, headers=headers, tablefmt="grid"))
        elif inputparameters[2] == "completed":
            headers = ["Order ID", "Time ordered", "Completed", "Total price"]
            cursor.execute("SELECT o.order_id, o.datetime_ordered, o.completed, sum(oi.quantity * i.price) AS total_cost FROM orders o JOIN ordered_items oi ON oi.order_id = o.order_id JOIN items i ON oi.item_id = i.item_id WHERE o.customer_id = %s AND o.completed = 1 GROUP BY o.order_id", (customer_id[0],))
            data = [row for row in cursor.fetchall()]
            print(tabulate(data, headers=headers, tablefmt="grid"))
        elif inputparameters[2] == "uncompleted":
            headers = ["Order ID", "Time ordered", "Completed", "Total price"]
            cursor.execute("SELECT o.order_id, o.datetime_ordered, o.completed, sum(oi.quantity * i.price) AS total_cost FROM orders o JOIN ordered_items oi ON oi.order_id = o.order_id JOIN items i ON oi.item_id = i.item_id WHERE o.customer_id = %s AND o.completed = 0 GROUP BY o.order_id", (customer_id[0],))
            data = [row for row in cursor.fetchall()]
            print(tabulate(data, headers=headers, tablefmt="grid"))

    elif inputparameters[1] == "details":
        if len(inputparameters) == 3:
            cursor.execute("SELECT i.item_name, oi.quantity, i.price, (oi.quantity * i.price) AS total_cost FROM ordered_items oi JOIN orders o ON oi.order_id = o.order_id JOIN items i ON oi.item_id = i.item_id WHERE o.customer_id = %s AND oi.order_id = %s", (customer_id[0], inputparameters[2],))
            data = [row for row in cursor.fetchall()]
            headers = ["Item name", "Amount", "Price", "Total price"]
            print(f"Displaying items from order {inputparameters[2]}")
            print(tabulate(data, headers=headers, tablefmt="grid"))
        else:
            print("You need to enter the id of the order")
    else:
        print("Error: command not found. Use help to learn how to use the commands!")
    
            
def store(customer_id, inputparameters):
    if inputparameters[1] == "all":
        cursor.execute("SELECT * FROM items")
        data = [row for row in cursor.fetchall()]
        headers = ["Item ID", "Category", "Name", "Manufacturer", "Description", "Stock", "Price"]
        print(tabulate(data, headers=headers, tablefmt="grid"))
    elif inputparameters[1] == "category":
        cursor.execute("SELECT * FROM items WHERE category = %s", (inputparameters[2],))
        data = [row for row in cursor.fetchall()]
        headers = ["Item ID", "Category", "Name", "Manufacturer", "Description", "Stock", "Price"]
        print(tabulate(data, headers=headers, tablefmt="grid"))
    elif inputparameters[1] == "manufacturer":
        cursor.execute("SELECT * FROM items WHERE manufacturer = %s", (inputparameters[2],))
        data = [row for row in cursor.fetchall()]
        headers = ["Item ID", "Category", "Name", "Manufacturer", "Description", "Stock", "Price"]
        print(tabulate(data, headers=headers, tablefmt="grid"))
    elif inputparameters[1] == "list":
        if len(inputparameters) == 3 and inputparameters[2] == "category":
            cursor.execute("SELECT DISTINCT category FROM items")
            print("The following are the categories available in the store.")
            [print(row[0]) for row in cursor.fetchall()]
            print("Use 'store category your-category', to filter the store by category.")
        elif len(inputparameters) == 3 and inputparameters[2] == "manufacturer":
            print("The following are the manufacturers available in the store.")
            cursor.execute("SELECT DISTINCT manufacturer FROM items")
            [print(row[0]) for row in cursor.fetchall()]
            print("Use 'store category your-category', to filter the store by category.")
        else:
            print("error: you need to enter 'category' or 'manufactrer' to use the store list command.")
    else:
        print("Error: command not found. Use help to learn how to use the commands!")
    
        
def adminhelp():
    print("Admin help")
    print("additem: add item(s) to the store")
    print("updatestock [item_id] [amount_to_add]: add more stock")
    print("listuncompleted: list all uncompleted orders")
    print("listcompleted: list all completed orders")
    print("listall: list all orders")
    print("listcontent: list list the content of an order")
    print("markcomplete [order_id]: mark an order as complete")
    print("listcustomers: list all customers and their information")
    print("store")
    print("\tstore all: list all items available in the store")
    print("\tstore list: list all filters")
    print("\tstore category: list all categories in the store")
    print("\tstore category [catecory name]: list all available under a specified category")
    print("\tstore manufacturer: list all manufacturers in the store")
    print("\tstore manufacturer [manufacturer name]: list all items from a specified manufacturers")
    


print("Welcome to the shop for enter help")
print("To register an account write register")
while (True):
    print("Enter your name!")
    nameinput = input()
    if nameinput == "exit":
        break

    elif nameinput == "register":
        print("Enter all the following information separating them bye a pipe meaning |.")
        print("Name, Phone number, email, address")
        cmdinput = input().split("|")
        cursor.execute("INSERT INTO customers (name, phone_number, email, address) VALUES (%s, %s, %s, %s)", cmdinput)
        connection.commit()
        print(f"User added")

    elif nameinput == "admin":
        print("Welcome to the admin panel")
        while (True):
            print("")
            cmdinput = input().split()
            if cmdinput[0] == "exit":
                break
            elif cmdinput[0] == "help":
                adminhelp()
            elif cmdinput[0] == "additem":
                print("Enter all the following information separating them bye a pipe meaning |.")
                print("category, item_name, manufacutrer, description, stock, price")
                cmdinput = input().split("|")
                cursor.execute("INSERT INTO items (category, item_name, manufacturer, description, stock, price) VALUES (%s, %s, %s, %s, %s, %s)", cmdinput)
                connection.commit()
                print(f"User added")
            elif cmdinput[0] == "updatestock":
                cursor.execute("UPDATE items SET stock = stock + %s WHERE item_id = %s", (cmdinput[2], cmdinput[1]))
                connection.commit()
                print(f"Updated stock")
            elif cmdinput[0] == "listuncompleted":
                headers = ["Order ID", "Customer_ID", "Time ordered", "Completed", "Total price"]
                cursor.execute("SELECT o.order_id, o.customer_id, o.datetime_ordered, o.completed, sum(oi.quantity * i.price) AS total_cost FROM orders o JOIN ordered_items oi ON oi.order_id = o.order_id JOIN items i ON oi.item_id = i.item_id WHERE completed = 0 GROUP BY o.order_id")
                data = [row for row in cursor.fetchall()]
                print(tabulate(data, headers=headers, tablefmt="grid"))
            elif cmdinput[0] == "listcompleted":
                headers = ["Order ID", "Customer_ID", "Time ordered", "Completed", "Total price"]
                cursor.execute("SELECT o.order_id, o.customer_id,o.datetime_ordered, o.completed, sum(oi.quantity * i.price) AS total_cost FROM orders o JOIN ordered_items oi ON oi.order_id = o.order_id JOIN items i ON oi.item_id = i.item_id WHERE completed = 1 GROUP BY o.order_id")
                data = [row for row in cursor.fetchall()]
                print(tabulate(data, headers=headers, tablefmt="grid"))
            elif cmdinput[0] == "listall":
                headers = ["Order ID", "Customer_ID", "Time ordered", "Completed", "Total price"]
                cursor.execute("SELECT o.order_id, o.customer_id,o.datetime_ordered, o.completed, sum(oi.quantity * i.price) AS total_cost FROM orders o JOIN ordered_items oi ON oi.order_id = o.order_id JOIN items i ON oi.item_id = i.item_id GROUP BY o.order_id")
                data = [row for row in cursor.fetchall()]
                print(tabulate(data, headers=headers, tablefmt="grid"))
            elif cmdinput[0] == "listcontent":
                cursor.execute("SELECT i.item_name, oi.quantity, i.price, (oi.quantity * i.price) AS total_cost FROM ordered_items oi JOIN orders o ON oi.order_id = o.order_id JOIN items i ON oi.item_id = i.item_id WHERE oi.order_id = %s", (cmdinput[1],))
                data = [row for row in cursor.fetchall()]
                headers = ["Item name", "Amount", "Price", "Total price"]
                print(f"Displaying items from order {cmdinput[1]}")
                print(tabulate(data, headers=headers, tablefmt="grid"))
            elif cmdinput[0] == "markcomplete":
                cursor.execute("UPDATE orders SET completed = 1 WHERE order_id = %s", (cmdinput[1],))
                connection.commit()
                print(f"Marked order {cmdinput[1]} as complete.")
            elif cmdinput[0] == "listcustomers":
                cursor.execute("SELECT * FROM customers")
                data = [row for row in cursor.fetchall()]
                headers = ["Customer ID", "Name", "Phone Number", "Email", "Address"]
                print(tabulate(data, headers=headers, tablefmt="grid"))
            elif cmdinput[0] == "store":
                store([0], cmdinput)



    else:
        cursor.execute("SELECT customer_id FROM customers WHERE name = %s", (nameinput,))
        customer_id = cursor.fetchone()
        if customer_id:
                print(f"Welcome {nameinput}!")
                print(f"Use help to get with all the commands!")
                while (True):
                    print("")
                    cmdinput = input().split()
                    if cmdinput[0] == "exit":
                        break
                    
                    elif cmdinput[0] == "help":
                        getcmdhelp()
                        
                    elif cmdinput[0] == "cart":
                        cart(customer_id, cmdinput)

                    elif cmdinput[0] == "order":
                        order(customer_id, cmdinput)
                    elif cmdinput[0] == "store":
                        store(customer_id, cmdinput)
                        
                    else:
                        print("Error: unrecognized command, use help to get a list of all avilable commands.")
