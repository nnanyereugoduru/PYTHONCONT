for i in range(1,20):
    print(f'{i:2d} |', end=" " )
    for j in range(1,20):
        print(f'{i * j:4d}', end=' ')
    print()