import os
import requests
from bs4 import BeautifulSoup
import mutagen.id3
from mutagen.easyid3 import EasyID3


def getPath():
    path = input('Path: ')
    with open('constants.py', 'w') as file:
        file.write("PATH = r'" + path + "'")


try:
    import constants
except ImportError:
    print("No path file detected. Enter music path below.")
    getPath()
    import constants


directory = constants.PATH

for filename in os.listdir(directory):
    print("Old Title: {}".format(filename))
    search_name = filename.replace(" ", "+")
    search_name = filename.replace(".", "+")
    search_name = filename.replace("mp3", "+")
    r = requests.get(
        'https://www.google.com/search?q={}+metrolyrics'.format(search_name))
    soup = BeautifulSoup(r.text, "html.parser")
    search_title = soup.find_all('h3')[0]

    link_text = search_title.get_text().replace("\u2013", "-")
    if link_text.endswith("MetroLyrics"):
        new_title = link_text[:-18] + ".mp3"
        print("New Title: {}".format(new_title))
        os.rename(
            os.path.join(directory, filename),
            os.path.join(directory, new_title)
        )

    tag_path = directory + '\\' + str(new_title)

    try:
        song = EasyID3(tag_path)
    except mutagen.id3.ID3NoHeaderError:
        song = mutagen.File(tag_path, easy=True)
        song.add_tags()

    song['title'] = new_title.split(" - ")[1].split(".")[0]
    song['artist'] = new_title.split(" - ")[0]
    song.save()
    changed = EasyID3(tag_path)
    print(changed)
