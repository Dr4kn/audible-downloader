# Introduction
A Dockercontainer that automatically downloads, converts your audible audiobooks from aax to m4b.

The Programm checks every 6h if there are new books in you library.

Audiobooks can be either be just their file or ordered directly into folders. This can benefical for large libraries or usage with other programs.
The directory structure uses the [audiobookshelf](https://www.audiobookshelf.org/docs#book-directory-structure) convention. 
Author/Series/audiobook.m4b or Author/audiobook.m4b if a Series doesn't exist.

## First time running
Create a `login.ini` file in your home directory e.g.: `~/.config/audible/login.ini`. You can create the folder yourself or let the program run once to create them.

Put this Information into it:
```<the email you use for your (amazon) account>
<your password>
<your country code https://audible.readthedocs.io/en/latest/marketplaces/marketplaces.html#country-codes>
<False>
```

Activate 2 Factor Authentication for your amazon account if you don't have it already turned on.
Run the script and it will prompt you in the commandline for a Code.
Type in your auth code your received or have in your Authenticator app and press enter.
Now Multiple Files should have appeared.