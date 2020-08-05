# Python Podcast to YouTube

Will need `<item> <image href="url.jpg"></item>`!!!!!
https://medium.com/@osanda.deshan/getting-google-oauth-access-token-using-google-apis-18b2ba11a11a

## Basic Overview
This program parses podcast RSS feeds, converts audio episodes to videos, and uploads each video to a YouTube channel playlist. 

## What You Need
- Google Developer client_secrets.json to use YouTube API V3
- A podcast RSS feed with this format: https://feeds.kpbs.org/cinema-junkie
- The YouTube Playlist ID where the video should be inserted

## How to Use It
- `pip install -r requirements.txt`
- `python main.py [RSS feed URL] [YouTube Playlist ID]`

## More Details
The video is created using the RSS feed. It takes the episode image and overlays the show logo on the top left corner. The video output is an mkv file. 