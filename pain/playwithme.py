'''while True:
    a = int(input("Enter a decimal number: "))
    b = bin(a)[2:]  
    print(f" {b}") # Convert to binary and remove the '0b' prefix'''

while True:
    a = input("enter bin: ")
    b = int(a,2)
    print(b)

#for char in 'Nnanyereugo':
#    print(f"{char!r} → {ord(char)}")

binary_string = "01000011 01101111 01101101 01110000 01110101 01110100 01100101 01110010 00100000 01010011 01100011 01101001 01100101 01101110 01100011 01100101"

result = ''.join(chr(int(b, 2)) for b in binary_string.split())
print(result)