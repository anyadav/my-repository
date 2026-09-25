#!/usr/bin/python
#calculator program
#this variable tells the loop whether it should loop or not.
# 1 means loop. anything else means don't loop.

loop = 1

#this variable holds the user's choice in the menu:

choice = 0

while loop == 1:
    #print what options you have
    print("Welcome to calculator.py")

    print("your options are:")
    print(" ")
    print("1) Addition")
    print("2) Subtraction")

    print("3) Multiplication")

    print("4) Division")
    print("5) Quit calculator.py")
    print(" ")

    choice = int(input("Choose your option: "))
    if choice == 1:
        add1 = int(input("Add this: "))
        add2 = int(input("to this: "))
        print(add1, "+", add2, "=", add1 + add2)
    elif choice == 2:
        sub2 = int(input("Subtract this: "))
        sub1 = int(input("from this: "))
        print(sub1, "-", sub2, "=", sub1 - sub2)
    elif choice == 3:
        mul1 = int(input("Multiply this: "))
        mul2 = int(input("with this: "))
        print(mul1, "*", mul2, "=", mul1 * mul2)
    elif choice == 4:
        div1 = int(input("Divide this: "))
        div2 = int(input("by this: "))
        if div2 == 0:
            print("trying to divide by 0")
        else:
            print(div1, "/", div2, "=", div1 / div2)
    elif choice == 5:
        loop = 0

print("Thankyou for using calculator.py!")
