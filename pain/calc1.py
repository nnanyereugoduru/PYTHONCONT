import numpy as np
import re

# calculator script that solves math

def algebr_1(x,y, equation):
    equation = equation.lower()
    equation = equation.replace('x', str(x))
    equation = equation.replace('y', str(y))
    equation = equation.replace('^', '**')
    equation_solve = float(eval(equation))
    return equation_solve

def split_rquation(equation):
    numbers = [float(x) for x in re.findall(r'[+-]?\d+\.?\d*', equation)]
    return numbers

def linear_solve(list_one, list_two):
    A = np.array([list_one[:2],list_two[:2]]) #np only takes in one arguement
    B = np.array([list_one[2], list_two[2]])
    
    d = np.linalg.det(A)
    if abs(d) < 1e-10: # zero
        A1 = np.column_stack([A,B])
        if np.linalg.matrix_rank(A) == np.linalg.matrix_rank(A1):
                return "inifinite"
        else:
                return "does not eiste"
    
    solution = np.linalg.solve(A, B)
    return solution 
def hex_convert(num, target_base):
     if num == 0:
            return "0"
     digits = '0123456789ABCDEF'
     result = ''
     while num > 0:
      result = digits[num % target_base] + result
      num //= target_base
     return result

online = True
online_count = 0
while online:
    if online_count < 1:
        print("Welcome to Calc1, new installment of an advanced calc. ")
        online_count += 1
    print("1. algebra")
    print("2. solve for x,y")
    print("3. hexadecimal conversionn for decimal to binary or octal")
    print("4. addition and binary subtraction")
    descision = int(input(" "))
    if descision == 1:
        user_input = float(input("Enter x:"))
        user_input1 = float(input("Enter y: "))
        user_input2 = input("Enter the algebraic equation")
        user_input3 = int(input("decimal level "))

        result = algebr_1(user_input, user_input1, user_input2)
        print(f"{result:.{user_input3}f}")
    elif descision == 2:
        ''' 
            5x -2y = -2
        a1   b1   c1
        3x +4y = 30
        goal is to use both equations to find if there is an intercept, goes to infinty or does not exist.
        s = {(2,6)}  
        '''
        equation_1 = input("enter equation one ").strip()
        equation_2 = input("enter equation two ").strip()

        b = split_rquation(equation_1)
        a = split_rquation(equation_2)

        #print(a)
        sol = linear_solve(b, a)
       
        print(f"solution = ({sol})")
    elif descision == 3:
        user_input = input("Enter hexadecimal number: ")
        num = int(user_input,16)
        user_input1 = int(input("Enter target base: "))
        result = hex_convert(num, user_input1)
        if result is None:
            print("Invalid target base.")
        else:
            print(f"result = {result}")


    elif descision == 4:
        user_input = input("Enter first number: ")
        user_input1 = input("Enter second number: ")
        user_input2 = input("Enter operation (+ or -): ")
        num_1 = int(user_input,2)
        num_2 = int(user_input1,2)
        if user_input2 == "+":
            result = num_1 + num_2
            print()
            print(f"result = {bin(result)[2:]} , {result}") # the [2:] is to remove the '0b' prefix that Python adds to binary numbers
            input("press enter to continue")
        elif user_input2 == "-":
            result = num_1 - num_2
            print()
            print(f"result = {bin(result)[2:]} , {result}")
            input("press enter to continue")
        else:
            print("Invalid operation. Please enter '+' or '-'.")
         
       

        




    