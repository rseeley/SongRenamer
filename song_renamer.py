#! python

import os
import requests
from bs4 import BeautifulSoup
import mutagen.id3
from mutagen.easyid3 import EasyID3


def getPath():
    """
    Gets path to music files needing updated and stores in constants.py.  If
    constants.py isn't available, it will be created.
    """

    print("No path file detected. Enter music path below.")
    path = input('Path: ')
    with open('constants.py', 'w') as file:
        file.write("PATH = r'" + path + "'")


# Import constants file, if available
# If file isn't found (ImportError), call getPath() to get user credentials
try:
    import constants
except ImportError:
    getPath()
    import constants


def songRenamer():
    """
    Main function for renaming music in the given directory. If tags aren't
    already available on the songs, they will be added.
    """

    # Get path from constants.py
    directory = constants.PATH

    # For each file in the directory, search Google for the filename, rename
    # the song, and add tags
    for filename in os.listdir(directory):
        print("Old Title: {}".format(filename))

        # Replace spaces, periods, and the file type from the search term.
        # This ensures the correct link will show up every time.
        search_name = filename.replace(" ", "+")
        search_name = filename.replace(".", "+")
        search_name = filename.replace("mp3", "+")

        # Search Google for the filename
        r = requests.get(
            'https://www.google.com/search?q={}+metrolyrics'
            .format(search_name))

        # Use BeautifulSoup to parse the search result link titles
        soup = BeautifulSoup(r.text, "html.parser")
        search_title = soup.find_all('h3')[0]

        # This is a compatibility fix for an issue in Python
        link_text = search_title.get_text().replace("\u2013", "-")

        # Get the link that ends with 'MetroLyrics'
        if link_text.endswith("MetroLyrics"):
            # Slices the link text to remove unnecessary text and adds the file
            # type.
            new_title = link_text[:-18] + ".mp3"
            print("New Title: {}".format(new_title))

            # Rename the file
            os.rename(
                os.path.join(directory, filename),
                os.path.join(directory, new_title)
            )

        # Create the new path for tagging purposes
        tag_path = directory + '\\' + str(new_title)

        # Set up tags to be added later
        try:
            song = EasyID3(tag_path)
        except mutagen.id3.ID3NoHeaderError:
            song = mutagen.File(tag_path, easy=True)
            song.add_tags()

        # Get the title and artist from the new title and save them as tags
        song['title'] = new_title.split(" - ")[1].split(".")[0]
        song['artist'] = new_title.split(" - ")[0]
        song.save()
        changed = EasyID3(tag_path)
        print(changed)


if __name__ == '__main__':
    songRenamer()
