import json
import os
import random


class Song:
    def __init__(self, title , rating):
        # store title and rating as instance variables
        self.title = title
        self.rating = rating
    
    def display(self):
        # print the song title and rating
        print(f"{self.title} : {self.rating}")

    
    def update_rating(self, new_rating):
        # update the rating, use ratecheck logic here
        if new_rating > 5:
            new_rating = 5
        elif new_rating < 0:
            new_rating = 0
        self.rating = new_rating


class Catalog:
    def __init__(self):
        # what data structure holds all the artists and songs?
        self.data= {}   
    def add(self, artist, title, rating):
        new_song = Song(title, rating)

        if artist not in self.data:
            self.data[artist] = [new_song]
        else:
            existing_title = [song.title for song in self.data[artist]]
            if title not in existing_title:
                self.data[artist].append(new_song)

    def view(self):
        # display all artists and their songs
        for artist, songs in self.data.items():
            print(f'\n{artist}' , end= " ")
            for song in songs:
                song.display()
    
    def randomize(self):
        # pick a random artist and song
        if not self.data:
            print("empty catalog")
            return
        else:
            artist =  random.choice(list(self.data.keys()))
            song = random.choice(list(self.data[artist]))
            
            print(f' A random song will be {song.title} by {artist} with a rating of {song.rating : .2f}')
    
    def update_rating(self, artist, title, new_rating):
        # find the song and update its rating
        if artist not in self.data:
            print('artist not found')
            return
        for song in self.data[artist]:
            if song.title == title:
                song.update_rating(new_rating)
                print('updated')
                return
        print('song not found')
    
      
    def save(self, path):
        saveable = {}

        for artist, songs in  self.data.items():
            saveable[artist] = [{"title" : s.title, "rating" : s.rating} for s in songs ]
        with open(path, 'w') as file:
            json.dump(saveable, file,indent=4)
        print("saved")
    
    def load(self, path):
        if os.path.exists(path):
            with open(path, 'r') as file:
                raw = json.load(file)

            for artist, songs in raw.items():
                self.data[artist] = [Song(s["title"], s["rating"]) for s in songs] 
        else:
            self.data = {}
            with open(path,'w') as file:
                json.dump(self.data, file, indent=4)

def main():
    path = r'C:\Projects\FOLDER1\PY1\pain\catalog.json'
    catalog = Catalog()
    catalog.load(path)

    online = True
    count = 0

    while online:
        try:
            if count <= 0:
                print("Welcome to the music catalog software!")
                count += 1
            print("\n1. Add album")
            print("2. View catalog")
            print("3. Randomize")
            print("4. Update rating")
            print("5. Exit")
            choice = input(">> ")

            if choice == "1":
                artist = input("artist: ").lower().strip()
                title = input("album: ")
                rating = float(input("rating (0-5): "))
                catalog.add(artist, title, rating)
                catalog.save(path)

            elif choice == "2":
                catalog.view()

            elif choice == "3":
                catalog.randomize()

            elif choice == "4":
                artist = input("artist: ").lower().strip()
                title = input("album: ")
                new_rating = float(input("new rating (0-5): "))
                catalog.update_rating(artist, title, new_rating)
                catalog.save(path)

            elif choice == "5":
                online = False
                print("Goodbye!")

            else:
                print("invalid")

        except ValueError:
            print("invalid input")
            

if __name__ == '__main__':
    main()