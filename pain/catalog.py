'''the goal is to create a music catalog software'''
import os
import json
import random

def ratecheck(rating):
    if rating > 5:
        rating = 5
    elif rating < 0:
        rating = 0
    return rating
    
path = r'C:\Projects\FOLDER1\PY1\pain\catalog.json'

def save():
    with open(path, 'w') as file:
        json.dump(catalog, file, indent=4)
    print("saved")


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
    try:
        if count <= 0:
            print("Welcome to the music catalog software!")
            count += 1
            
        print("\n1. Add a new album")
        print("2. View catalog")
        print("3. Exit")
        print("4. randomize")
        print("5. update ratings")
        choice = input("Enter your choice: ")

        if choice == "1":
            print('warning the codes automatically saves artist in their lowercase form')
            print("All questions must be answered ")
            print()
            title = input("Enter album title: ")
            if not title:
                print('invalid')
                continue     
            artist = input("Enter artist name: ").lower()
            rating = float(input("enter rating lowest 0, max 5: "))
            rating = ratecheck(rating)
            if not artist:
                print('invalid')
                continue

            if artist not in catalog:
                catalog[artist] = {}
                catalog[artist][title] = rating
            elif artist in catalog:
                if title not in catalog[artist]:
                    catalog[artist][title] = rating  
            save()

        elif choice == "2":
            if not catalog:
                print("Catalog is empty.")
            else:
                print("the songs in this collection are:")
                for artist, song in catalog.items():
                    print(f'\n{artist} : ', end='')
                    for song, rating in song.items():
                        
                        print(f'\n\t {song} : {rating :.2f}')
                        # print(f'\n : {song }{rating}')
        elif choice == "3":
            online = False
            print("Exiting the music catalog software. Goodbye!")

        elif choice == "4":
            if not catalog:
                print("catalog does not exist")
                continue
            artist = random.choice(list(catalog.keys()))
            song = random.choice(list(catalog[artist].keys()))
            print(f'Random pick: {song} by {artist}')

        elif choice == "5":
            check_artist = input("enter artist: ").lower().strip()
            if check_artist not in catalog:
                print("invalid")
            else:
                for song , ratings in catalog[check_artist].items():
                    print(f'{song} : {ratings :.2f}')
                   # print({song})
                change_rating = input("what song u want to change: ")
                if change_rating not in catalog[check_artist]:
                    print("invalid")
                else:
                    new_rating = float(input("what is the new rating: "))
                    new_rating = ratecheck(new_rating) # made the function cause it looks like I would write the rate check twice     
                    catalog[check_artist][change_rating] = new_rating
                    save()

            
        else:
            print("Invalid choice. Please try again.")
    except ValueError:
       print("invalid due to value error")

'''
{artist name : {song:rating, song:rating, song:rating}}
'''

    

    