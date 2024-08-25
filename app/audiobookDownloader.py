import json
import os
import subprocess
import sqlite3
import csv


config = "/config"
audiobook_download_directory = "/downloads"
audiobook_directory = "/audiobooks"
use_folders = True if os.getenv('AUDIOBOOK_FOLDERS').lower() == "true" else False

con = sqlite3.connect(config + "/audiobooks.db")
with con:
	con.execute("""CREATE TABLE IF NOT EXISTS audiobooks (
                asin TEXT UNIQUE,
                title TEXT NOT NULL,
			 	subtitle TEXT,
			 	authors TEXT NOT NULL,
			 	series_title TEXT,
				narrators TEXT,
			 	series_sequence INT,
				release_date TEXT,
                downloaded INT
        );""")

# program exits and errors if it can't get the activation bytes
subprocess.run(["audible", "activation-bytes"])
results = [each for each in os.listdir(config) if each.endswith('.json')]
activation_bytes = json.load(open(config + "/" + results[0]))["activation_bytes"]
if activation_bytes is None:
	print("error: no activation bytes found exiting")
	exit()



# get library from audible cli
# update db with all new titles
def update_titles():
	subprocess.run(["audible", "library", "export"])
	file = lines = open("library.tsv")
	reader = csv.DictReader(file, delimiter='\t')
	cur = con.cursor()

	for row in reader:
		values = [row['asin'], row['title'], row['subtitle'], row['authors'], row['series_title'], row['narrators'], row['series_sequence'], row['release_date'], 0]
		if cur.execute('SELECT * FROM audiobooks WHERE asin=?', [row['asin']]).fetchone() is None:
			cur.execute('insert into audiobooks values(?, ?, ?, ?, ?, ?, ?, ?, ?)', values)
	con.commit()

def create_audiobook_folder(asin):
	cur = con.cursor()
	book = cur.execute('SELECT authors, title, series_title, subtitle, narrators, series_sequence, release_date FROM audiobooks WHERE asin=?', [asin]).fetchone()
	authors = book[0]

	title = book[1]
	series_title = book[2]
	subtitle = book[3]
	narrators = book[4]
	series_sequence = book[5]
	release_date = book[6]

	directory = audiobook_directory + "/" + authors + "/"
	if series_title: # if series title exists the sequence also exists
		directory = directory + series_title + "/" + str(series_sequence) + " - "
	directory = directory + release_date.split("-")[0] + " - " + title
	if subtitle:
		directory = directory + " - " + subtitle
	directory = directory + " {" + narrators + "}" + "/"

	os.makedirs(os.path.dirname(directory), exist_ok=True)

	return directory

def download_new_titles():
	cur = con.cursor()
	to_download = cur.execute('SELECT asin FROM audiobooks WHERE downloaded=?', [0]).fetchall()

	for asin in to_download:
		subprocess.run(["audible", "download", "-a", asin[0], "--aax", "--timeout", "0", "-f", "asin_ascii", "--ignore-podcasts", "-o", audiobook_download_directory])

		# if files were downloaded but were not yet decoded they can be pushed into the wrong folder
		# it's to much work for very rare or a none existant failure that can be fixed by a bit of manual labor
		audiobooks = [each for each in os.listdir(audiobook_download_directory) if each.endswith('.aax')]
		for audiobook in audiobooks:
			new_asin = audiobook.split("_")[0]
			asin_check = cur.execute("Select title FROM audiobooks WHERE asin=?", [new_asin]).fetchone()
			if asin_check is None:
				new_name = audiobook.replace(new_asin, asin[0])
				os.rename(audiobook_download_directory + "/" + audiobook, audiobook_download_directory + "/" + new_name)
				audiobook = new_name

			asin = audiobook.split("_")[0]

			# create folders after the audiobookshelf convention
			cur.execute('UPDATE audiobooks SET downloaded = 1 WHERE asin = ?', [asin])
			con.commit()

			src = audiobook_download_directory + "/" + audiobook
			des = create_audiobook_folder(asin) + audiobook[:-3] + "m4b" if use_folders else audiobook_directory + "/"  + audiobook[:-3] + "m4b"
			subprocess.run(["ffmpeg", "-activation_bytes", activation_bytes, "-i", src, "-c", "copy", des])
			os.remove(src)
		
def main():
	update_titles()
	download_new_titles()

if __name__ == "__main__":
	main()
