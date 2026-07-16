import sqlite3
import os

db_path = r'C:\Projects\FOLDER1\PY1\pain\movies.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# directors table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS directors (
        id INTEGER PRIMARY KEY,
        name TEXT,
        nationality TEXT,
        birth_year INTEGER
    )
''')

# movies table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY,
        title TEXT,
        genre TEXT,
        year INTEGER,
        rating REAL,
        box_office_million REAL,
        director_id INTEGER
    )
''')

# clear tables first to avoid duplicates on rerun
cursor.execute("DELETE FROM movies")
cursor.execute("DELETE FROM directors")

directors = [
    (1, 'Christopher Nolan', 'British', 1970),
    (2, 'Martin Scorsese', 'American', 1942),
    (3, 'Quentin Tarantino', 'American', 1963),
    (4, 'Steven Spielberg', 'American', 1946),
    (5, 'Denis Villeneuve', 'Canadian', 1967),
    (6, 'Ridley Scott', 'British', 1937),
    (7, 'James Cameron', 'Canadian', 1954),
    (8, 'David Fincher', 'American', 1962),
    (9, 'Wes Anderson', 'American', 1969),
    (10, 'Jordan Peele', 'American', 1979),
]

movies = [
    (1, 'The Dark Knight', 'Action', 2008, 9.0, 1005.0, 1),
    (2, 'Inception', 'Sci-Fi', 2010, 8.8, 836.8, 1),
    (3, 'Interstellar', 'Sci-Fi', 2014, 8.6, 773.0, 1),
    (4, 'Oppenheimer', 'Drama', 2023, 8.9, 952.0, 1),
    (5, 'Goodfellas', 'Crime', 1990, 8.7, 46.8, 2),
    (6, 'The Departed', 'Crime', 2006, 8.5, 290.0, 2),
    (7, 'Pulp Fiction', 'Crime', 1994, 8.9, 214.0, 3),
    (8, 'Inglourious Basterds', 'War', 2009, 8.3, 321.0, 3),
    (9, 'Django Unchained', 'Western', 2012, 8.4, 425.0, 3),
    (10, 'Schindlers List', 'Drama', 1993, 8.9, 322.0, 4),
    (11, 'Jurassic Park', 'Adventure', 1993, 8.1, 1046.0, 4),
    (12, 'Saving Private Ryan', 'War', 1998, 8.6, 482.0, 4),
    (13, 'Dune', 'Sci-Fi', 2021, 8.0, 401.0, 5),
    (14, 'Dune Part Two', 'Sci-Fi', 2024, 8.8, 711.0, 5),
    (15, 'Arrival', 'Sci-Fi', 2016, 7.9, 203.0, 5),
    (16, 'Gladiator', 'Action', 2000, 8.5, 460.0, 6),
    (17, 'The Martian', 'Sci-Fi', 2015, 8.0, 630.0, 6),
    (18, 'Alien', 'Horror', 1979, 8.4, 104.0, 6),
    (19, 'Titanic', 'Romance', 1997, 7.9, 2201.0, 7),
    (20, 'Avatar', 'Sci-Fi', 2009, 7.8, 2923.0, 7),
    (21, 'Fight Club', 'Drama', 1999, 8.8, 101.0, 8),
    (22, 'Se7en', 'Thriller', 1995, 8.6, 327.0, 8),
    (23, 'Gone Girl', 'Thriller', 2014, 8.1, 369.0, 8),
    (24, 'The Grand Budapest Hotel', 'Comedy', 2014, 8.1, 175.0, 9),
    (25, 'Get Out', 'Horror', 2017, 7.7, 255.0, 10),
    (26, 'Us', 'Horror', 2019, 6.8, 255.0, 10),
    (27, 'Nope', 'Horror', 2022, 6.8, 123.0, 10),
    (28, 'Tenet', 'Action', 2020, 7.3, 365.0, 1),
    (29, 'The Wolf of Wall Street', 'Crime', 2013, 8.2, 392.0, 2),
    (30, 'Kill Bill Vol 1', 'Action', 2003, 8.1, 180.0, 3),
]

cursor.executemany("INSERT INTO directors VALUES (?, ?, ?, ?)", directors)
cursor.executemany("INSERT INTO movies VALUES (?, ?, ?, ?, ?, ?, ?)", movies)

conn.commit()
print(f"inserted {len(directors)} directors and {len(movies)} movies")
conn.close()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# check directors
cursor.execute('SELECT title, rating FROM movies ORDER BY  rating DESC ')
rows = cursor.fetchall()
for i, j in rows:
    print(f"{i} : {j}")
print()

cursor.execute('SELECT title, rating FROM movies WHERE rating > 8.5 ORDER BY rating DESC')
rows = cursor.fetchall()
for i,j in rows:
    print(f"{i} : {j}")
print()

cursor.execute('SELECT AVG(rating) FROM movies')
rows = cursor.fetchone()
print(f"{rows}")
print()

cursor.execute('SELECT genre, COUNT(*) as total FROM movies GROUP BY genre ORDER BY total DESC')
rows = cursor.fetchall()
for genre, total in rows:
    print(f"{genre}: {total} movies")
print()

cursor.execute('SELECT box_office_million, title FROM movies WHERE box_office_million > 500')
rows = cursor.fetchall()
for i, j in rows:
    print(f"${i}M : {j}")
print()

cursor.execute('SELECT SUM(box_office_million) as total, director_id FROM movies GROUP BY director_id ORDER BY total DESC ')
rows = cursor.fetchall()
for i,j in rows:
    print(f"${i}M : {j} ID")
print()

cursor.execute('SELECT director_id, COUNT(*) as total_movies FROM movies GROUP BY director_id HAVING COUNT(*) > 2 ORDER BY total_movies DESC')
rows = cursor.fetchall()
for i,j in rows:
    print(f"ID {i} : {j} movies")
print()

cursor.execute('SELECT movies.title, directors.name FROM movies INNER JOIN directors ON movies.director_id = directors.id ')
rows = cursor.fetchall()
for i,l in rows:
    print(f" {i} directed by {l}")
print()
cursor.execute('''
    SELECT d.name, COUNT(*) as movies, 
           ROUND(AVG(m.rating), 2) as avg_rating,
           SUM(m.box_office_million) as total_box_office
    FROM movies m
    INNER JOIN directors d ON m.director_id = d.id
    GROUP BY d.name
    ORDER BY avg_rating DESC
''')
rows = cursor.fetchall()
for row in rows:
    print(f"{row[0]:<20} {row[1]} movies  avg: {row[2]}  box office: ${row[3]}M")



conn.close()