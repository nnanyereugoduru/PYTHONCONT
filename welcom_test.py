import face_recognition

path = r"C:\Projects\FOLDER1\PY1\me2.jpg"

try:
    img = face_recognition.load_image_file(path)
    print("Loaded:", img.shape)
except Exception as e:
    print("ERROR:", e)
