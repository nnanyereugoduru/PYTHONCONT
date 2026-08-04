def calc(conditionA, number, type, conditionB, conditionC):
    a,b,f,e = 0,0,0,0
    
    if number > 100:
        a = number * 0.2
    elif number > 50:
        a = number * 0.1
    
    if type == "gold":
        b = 15
    elif type == "silver":
        b = 8
    elif type == "bronze":
        b = 3
    
    total = number - a - b

    if conditionB:
        if total > 0:
            e = total * 0.07
    if conditionC:
        f = 5

    final = total + e - f
    if final < 0:
        final = 0

    return final

def main():
    print(calc(True, 120, "gold", True, False))
    print(calc(False, 60, "silver", False, True))
    print(calc(True, 30, "bronze", True, True))
    print(calc(False, 200, "none", False, False))


if __name__ == "__main__":
    main()