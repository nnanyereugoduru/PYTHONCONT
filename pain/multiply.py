for i in range(1,13):
    print(f'{i:2d} |', end=" " )
    for j in range(1,13):
        print(f'{i * j:3d}', end=' ')
    print()