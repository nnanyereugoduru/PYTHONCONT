'''the goal is to create a music catalog software'''
import os
import json
import random

path = r'C:\Projects\FOLDER1\PY1\pain\catalog.json'

if os.path.exists(path):
        with open(path, 'r') as file:
            catalog = json.load(file)
else:
        catalog = {}
        with open(path, 'w' ) as file:
            json.dump(catalog, file, indent=4)

online = True
count = 0

while online:
    if count <= 0:
        print("Welcome to the music catalog software!")
        count += 1
        
    print("\n1. Add a new album")
    print("2. View catalog")
    print("3. Exit")
    print("4. randomize")
    choice = input("Enter your choice: ")

    if choice == "1":
        print('warning the codes automatically saves artist in their lowercase form')
        print()
        title = input("Enter album title: ")
        if not title:
             print('invalid')
             continue     
        artist = input("Enter artist name: ").lower()
        if not artist:
             print('invalid')
             continue
        if artist not in catalog:
             catalog[artist] = [title] 
        elif artist in catalog:
            if title not in catalog[artist]:
                catalog[artist].append(title) # the list already exist
        
        with open(path, 'w') as file:
            json.dump(catalog, file, indent=4)

    elif choice == "2":
        if not catalog:
            print("Catalog is empty.")
        else:
             print("the songs in this collection are:")
             for artist, song in catalog.items():
                  print(f'\n{artist} : ', end='')
                  print(', '.join(song))
    elif choice == "3":
        online = False
        print("Exiting the music catalog software. Goodbye!")

    elif choice == "4":
         if not catalog:
              print("catalog does not exist")
              continue
         artist = random.choice(list(catalog.keys()))
         song = random.choice(catalog[artist])
         print(f'Random pick: {song} by {artist}')
    else:
        print("Invalid choice. Please try again.")
        

    

    