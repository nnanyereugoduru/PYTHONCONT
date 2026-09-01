# convert characters to their corresponding ASCII values

def convert_to_ascii(input_string):
    ascii_values = [ord(char) for char in input_string]
    return ascii_values

a = convert_to_ascii("Nnanyereugo")
print([bin(x) for x in a])

NUM = [
101010000,
101100001,
101110100,
101110010,
101101001,
101100011,
101101011]

#rint([(x) for x in NUM])

num = 100101

b = 100101 // 10
c = 100101 // 100
print(b)
print(c)

