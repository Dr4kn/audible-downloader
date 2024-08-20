import json
import os
import subprocess
import sqlite3
import csv

con = sqlite3.connect("audiobooks.db")
with con:
	con.execute("""CREATE TABLE IF NOT EXISTS audiobooks (
                asin TEXT UNIQUE,
                title TEXT NOT NULL,
                subtitle TEXT,
				purchase_date TEXT,
                downloaded INT
			 	authors
			 	series_title
        );""")

# audible_directory = "/config"
audible_directory = "/home/adrian/.audible"
audiobook_directory = "/home/adrian/Music/"

# program exits and errors if it can't get the activation bytes
results = [each for each in os.listdir(audible_directory) if each.endswith('.json')]
activation_bytes = json.load(open(audible_directory + "/" + results[0]))["activation_bytes"]


# get library from audible cli
# update db with all new titles
def update_titles():
	subprocess.run(["audible", "library", "export"])
	file = lines = open("library.tsv")
	reader = csv.DictReader(file, delimiter='\t')
	cur = con.cursor()

	for row in reader:
		values = [row['asin'], row['title'], row['subtitle'], row['purchase_date'], 0]
		if cur.execute('SELECT * FROM audiobooks WHERE asin=?', [row['asin']]).fetchone() is None:
			cur.execute('insert into audiobooks values(?, ?, ?, ?, ?)', values)

	con.commit()

def download_new_titles():
	cur = con.cursor()
	to_download = cur.execute('SELECT asin FROM audiobooks WHERE downloaded=?', [0]).fetchall()

	if not to_download:
		exit()
	
	for asin in to_download:
		print("before")
		print(asin[0])
		subprocess.run(["audible", "download", "-a", asin[0], "--aax"])
		cur.execute('UPDATE audiobooks SET downloaded = 1 WHERE asin = ?', asin)
		con.commit()
		# if downloaded stuff is folder delete
		print("after")
		audiobooks = [each for each in os.listdir(audible_directory) if each.endswith('.aax')]
		for audiobook in audiobooks:
			src = audible_directory + "/" + audiobook
			des = audiobook_directory + audiobook[:-3] + "m4b"
			subprocess.run(["ffmpeg", "-activation_bytes", activation_bytes, "-i", src, "-c", "copy", des])
			os.remove(src)
		break
		
def main():
	# update_titles()
	download_new_titles()

if __name__ == "__main__":
	main()