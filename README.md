# Python Podcast to YouTube
This is a work in progress with some limitations, but it will work given the right RSS feed structure. 

## Basic Overview
This program parses podcast RSS feeds, converts audio episodes to videos, and uploads each video to a YouTube channel.
This is a work in progress with some limitations, but it will work given the right RSS feed structure. 

## What You Need
- Auth credentials to use YouTube API V3
- A podcast RSS feed with this format: https://feeds.kpbs.org/cinema-junkie 

# About YouTube Auth
- Follow these steps to get credentials: https://medium.com/@osanda.deshan/getting-google-oauth-access-token-using-google-apis-18b2ba11a11a
- Set the following evironment variables in your `.env` file: REFRESH_TOKEN, CLIENT_ID, CLIENT_SECRET

## How to Use It
- `pip install -r requirements.txt`
- `python main.py [RSS feed URL] [options]`
- `python main.py --help`

## More Details
The video is created using the RSS feed. It takes the episode image and overlays the show logo on the top left corner. The video output is an mkv file. 

The program will not work without episode images. Your `<item>` should include an `<[itunes]:image>` 