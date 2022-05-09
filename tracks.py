import re
import xml.etree.ElementTree as ET
import sqlite3
conn = sqlite3.connect('trackdb.sqlite')
cur = conn.cursor()

# Creating New Tables and delelting theme if they exist
cur.executescript("""--sql
                  
DROP TABLE IF EXISTS Artist;
DROP TABLE IF EXISTS Genre;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Track;

CREATE TABLE Artist(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, 
    name TEXT UNIQUE);

CREATE TABLE Genre(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT UNIQUE);
    
CREATE TABLE Album(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    artist_id INTEGER,
    title TEXT UNIQUE);
    
CREATE TABLE Track(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
   
    title TEXT UNIQUE,
    count INTEGER,
    rating INTEGER,
    len INTEGER,
    genre_id INTEGER,
    album_id INTEGER
    )"""
                  )


# Looks for the key field and if it matches then returns next text field which is our Data
# <key>Name</key><string>Another One Bites The Dust</string>

def lookup(track, key):
    found = False
    for data in track:
        if found:
            return data.text
        if data.tag == 'key' and data.text == key:
            found = True
    return None


# Reading xml and parsing it
fname = input("Enter file Name:")
if len(fname) < 1:
    fname = "library.xml"

#dict/dict /key /dict
stuff = ET.parse(fname)

# print(stuff)
tracks = stuff.findall('dict/dict/dict')  # A list of all tracks

# Looping through each(key) Track in the xml
for track in tracks:
    if (lookup(track, 'Track ID') is None):
        continue
    name = lookup(track, 'Name')
    artist = lookup(track, 'Artist')
    album = lookup(track, 'Album')
    genre = lookup(track, 'Genre')
    count = lookup(track, 'Play Count')
    rating = lookup(track, 'Rating')
    len = lookup(track, 'Total Time')

    # If the track has these missing parameters we will skip it
    if name is None or album is None or artist is None or genre is None:
        continue

    print(name, artist, genre, album, count, rating, len)

    # storing the retrieved data in relational Database

    # Artist Table
    cur.execute("INSERT OR IGNORE INTO Artist(name) VALUES(?)", (artist,))
    cur.execute("SELECT id FROM Artist WHERE name= ? ", (artist,))
    artist_id = cur.fetchone()[0]

    # Genre Table
    cur.execute("INSERT OR IGNORE INTO Genre(name) VALUES(?)", (genre,))
    cur.execute("SELECT id FROM Genre WHERE name = ?", (genre,))
    genre_id = cur.fetchone()[0]

    # Album Table
    cur.execute(
        "INSERT OR IGNORE INTO Album(title, artist_id) VALUES(?,?)", (album, artist_id))
    cur.execute("SELECT id FROM Album WHERE title = ? ", (album,))
    album_id = cur.fetchone()[0]

    # Track Table
    cur.execute('''
        INSERT OR REPLACE INTO Track(title,count, rating, len, genre_id, album_id ) 
        VALUES(?,?,?,?,?,?)''',
                (name, count, rating, len, genre_id, album_id))

conn.commit()  # commiting the changes to the database
