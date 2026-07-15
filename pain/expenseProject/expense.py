import os
import matplotlib.pyplot as plt
import json

#General goal is to make an expense app that saves to a json and can pull out a chart with the categories and respective share of the total

path = r'C:\Projects\FOLDER1\PY1\pain\expenseProject\expense.json'

def input_expenses(book):
    print('what is the category of ur input: ')
    user_cat = input('>> ').lower()
    print('what amount are you putting in')
    amount = float(input('>> '))
    if user_cat in book:
        book[user_cat] += amount
    else:
        book[user_cat] = amount

    
def check_expenses(book):
    print('1. regular')
    print('2. graph')
    user_input = int(input('>> '))

    if user_input == 1:
        for i, j in book.items():
            print(f'{i} : ${j:>8.2f}')
    elif user_input == 2:
        '''
        for this it seems like I am going to add the total amount
        get the total, get their individual divide them, show
        percentage and use that to create a chart
        '''
        ''' total = 0
        for i, j in book.items():
            total += j
        percentage = {}
        for i,j in book.items():
            percent = j/total * 100
            percentage[i] = percent'''
        
        plt.pie(book.values(), labels=book.keys(), autopct='%1.1f%%')
        plt.show()
        

    else:
        print()
        print('invalid')

online = True
count = 0
width = 40

if os.path.exists(path):
    with open(path, 'r') as file:
        expenses = json.load(file)
else:
    expenses = {}
    with open(path, 'w' ) as file:
        json.dump(expenses, file, indent=4)

while online:
    if count < 1:
            print('Welcome')
            count += 1
    try:
        print(f"{'EXPENSE PROGRAM':^{width}}")
        print(f"{'':=^{width}}")
        print(f"{'Menu':^{width}}")

        print('1. input expenses')
        print('2. check expenses')
        print('3. quit')
        
        user_input = int(input('CHOOSE (the number) >> '))

        if user_input == 1:
            input_expenses(expenses)
            with open(path, 'w') as file:
                json.dump(expenses, file, indent=4)
        elif user_input == 2:
            check_expenses(expenses)
        elif user_input == 3:
            print('goodbye')
            online = False
        else:
            print('invalid due to incorrect number')
            print()

    except ValueError:
        print()
        print('invalid due to incorrect value')