import json
import os
import subprocess

home_directory = os.environ['HOME']
audible_directory = os.environ['HOME'] + "/.audible"

def get_activation_bytes():
	results = [each for each in os.listdir(audible_directory) if each.endswith('.json')]
	file = json.load(open(audible_directory + "/" + results[0]))

	return(file["activation_bytes"])

def get_all_audiblefiles():
	return [each for each in os.listdir(audible_directory) if each.endswith('.aax')]
	
def main():
	activation_bytes = get_activation_bytes()
	
	for audiofile in get_all_audiblefiles():
		audiobook = audible_directory + "/" + audiofile
		subprocess.run(["ffmpeg", "-activation_bytes", activation_bytes, "-i", audiobook, "-c", "copy", audiobook[:-3] + "m4b"])
		print("finished")

if __name__ == "__main__":
	main()