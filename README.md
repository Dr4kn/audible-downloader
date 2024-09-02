# Introduction
A Dockercontainer that automatically downloads, converts your audible audiobooks from aax to m4b.

The Programm checks every 6h if there are new books in you library.

Audiobooks can be either be just their file or ordered directly into folders. This can benefical for large libraries or usage with other programs.
The directory structure uses the [audiobookshelf](https://www.audiobookshelf.org/docs#book-directory-structure) convention. 
Author/Series/audiobook.m4b or Author/audiobook.m4b if a Series doesn't exist.

# Run Image

## Build from source

Run in the Directory with the Dockerfile.
```
docker build -t audible-downloader .
```

List all images.
```
docker images ls
```

replace the container id with the your image hash
 
```
docker run -d \
	--name=audiobookDownloader \
	-e AUDIOBOOK_FOLDERS='True' \
	-v /path/to/audiobookDownloader/config:/config \
	-v /path/to/audiobookDownloader/audiobooks:/audiobooks \
	container id
```

## First time running
Run the container by one of the given methods.

List all running containers:

`docker ps`

Use the container shell:

`docker exec -it`

write:

`audible quickstart`

and answer the prompts.
The name of the auth file name doesn't matter but it can't be encrypted.
Login over the browser and copy the new URL back into the console after completing the captcha

## Build it yourself
`docker build -t audibleDownloader:1.0 .`
