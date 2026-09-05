# this is for ASCII image generation

from PIL import Image
import numpy as np


img = Image.open(r"C:\Projects\FOLDER1\PY1\pain\gtiPlay\#onepiece #luffy #monkeydluffy #anime #manga….jpg")
#img.show()
print(img.size)
print(img.mode)
img = img.resize((120, 60))

matrix_1 = np.array(img)
matrix_float = matrix_1.astype(np.float32)
matrix = matrix_float
height, width, channel = matrix.shape
pixel_list = []
for x in range(height):  # this does the same thing: pixel_list = list(img.getdata())
    for y in range(width):
        pixel = tuple(matrix[x][y])
        pixel_list.append(pixel)

brightness_list = []
#lightness_list = []
for i in pixel_list:
    b = sum(i) / len(i)
    #l = (max(pixel) + min(pixel))/ 2
    brightness_list.append(b)
    #lightness_list.append(l)

#print(brightness_list)
#new_birghtness_list = sorted(brightness_list)
unique_num = []

for i in brightness_list:
    if i not in unique_num:
        unique_num.append(i)
new_num = sorted(unique_num)


count_1 = 0
for i in new_num:
   #print(i)
   count_1 += 1
   

ascii_char = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

count = 0
for i in ascii_char:
    count += 1
#print(count)
#print(count_1)

max_b = max(brightness_list)   # should now be 255, or close to it

def brightness_to_char(b, ascii_chars, max_brightness):
    index = int(b / (max_brightness + 1) * len(ascii_chars))
    return ascii_chars[min(index, len(ascii_chars) - 1)]

ascii_result = [brightness_to_char(b, ascii_char, max_b) for b in brightness_list]

lines = []
for i in range(0, height, 2):
    line = "".join(ascii_result[i*width : (i+1)*width])
    lines.append(line)

as_art = "\n".join(lines)
print(as_art)