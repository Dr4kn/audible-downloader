import json
import os
import subprocess
import sqlite3
import csv
import re

# audible_directory = "/config"
audible_directory = "/home/adrian/.audible"

def get_activation_bytes():
	results = [each for each in os.listdir(audible_directory) if each.endswith('.json')]
	file = json.load(open(audible_directory + "/" + results[0]))

	return(file["activation_bytes"])

def get_all_audiblefiles():
	return [each for each in os.listdir(audible_directory) if each.endswith('.aax')]
	
def saveDownloadedFiles(audiblefiles):
	con = sqlite3.connect("audiobooks.db")
	cur.execute("CREATE TABLE audiobooks(asin, title, purchase_date)")

def test():
	audiobooks = [each for each in os.listdir(audible_directory) if each.endswith('.aax')]
	file = lines = open("library.tsv")
	reader = csv.DictReader(file, delimiter='\t')
	audio = audiobooks[0].split('-')[0]
	for row in reader:
		name = row['title'] + row['subtitle']
		name = re.sub(r'[ ,]+', '_', name)
		print(name)
		print(audio)
		print("\n")
		if audio == name:
			print(name)

	# for audio in audiobooks:
	# 	print(audio.split('-')[0])
	# print(audiobooks)



def main():
	# the programm kills itself if it can't find it, which is pretty much what I want regardless
	test()
	# activation_bytes = get_activation_bytes()

	
	# for audiofile in get_all_audiblefiles():
	# 	audiobook = audible_directory + "/" + audiofile
	# 	subprocess.run(["ffmpeg", "-activation_bytes", activation_bytes, "-i", audiobook, "-c", "copy", audiobook[:-3] + "m4b"])
	# 	print("finished")

if __name__ == "__main__":
	main()