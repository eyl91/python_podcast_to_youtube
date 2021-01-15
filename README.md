# Python Podcast to YouTube
This is a work in progress with some limitations, but it will work given the right RSS feed structure. 

## Basic Overview
This program parses podcast RSS feeds, converts audio episodes to videos, and can upload each video to a YouTube channel. 
## What You Need
- Auth credentials to use YouTube API V3
- A podcast RSS feed with this format: https://feeds.kpbs.org/cinema-junkie 

### About YouTube API V3
- Follow these [steps to get credentials](https://medium.com/@osanda.deshan/getting-google-oauth-access-token-using-google-apis-18b2ba11a11a)
- Your `.env` file should include:
```
REFRESH_TOKEN=
CLIENT_ID=
CLIENT_SECRET=
```

## How to Use It
- `pip install -r requirements.txt`
- `python main.py [RSS feed URL] [options]`
- `python main.py --help`

### Options
```
usage: main.py [-h] [-la LATEST]
               [-sep SPECIFIC_EPISODE [SPECIFIC_EPISODE ...]] [-lo]
               [-d DEFAULT_IMAGE] [-ot] [-lf] [-p] [-u]
               [-pid PODCAST_YOUTUBE_PLAYLIST_ID] [-cid YOUTUBE_CATEGORY_ID]
               [-t YOUTUBE_TAGS]
               podcast_feed

positional arguments:
  podcast_feed          Arg should be a link to the feed (i.e.,
                        https://feeds.kpbs.org/cinema-junkie) or path to an
                        xml file

optional arguments:
  -h, --help            show this help message and exit
  -la LATEST, --latest LATEST
                        Specify how many of the latest episodes (top being the
                        latest) should be uploaded to YouTube. Otherwise it
                        will parse all episodes.
  -sep SPECIFIC_EPISODE [SPECIFIC_EPISODE ...], --specific_episode SPECIFIC_EPISODE [SPECIFIC_EPISODE ...]
                        Pass specific episode title(s) to be uploaded to
                        YouTube
  -lo, --logo           Add if the podcast logo should be added over the
                        episode image.
  -d DEFAULT_IMAGE, --default_image DEFAULT_IMAGE
                        Set path for default image to be used for episodes.
  -ot, --overlay_text_episode_info
                        Text with episode information (Show Title, Episode
                        Title, Publication Date) to be overlayed on the image
  -lf, --local_file     Videos won't be uploaded to YouTube. It will be saved locally.
  -p, --youtube_private
                        Add if the podcast epsiodes uploaded to YouTube should
                        be set to private
  -u, --youtube_unlisted
                        Add if the podcast epsiodes uploaded to YouTube should
                        be set to unlisted
  -pid PODCAST_YOUTUBE_PLAYLIST_ID, --podcast_youtube_playlist_id PODCAST_YOUTUBE_PLAYLIST_ID
                        Arg should be the YouTube playlist ID this video will
                        be set to, it's also necessary to check what episodes
                        in the feed have already been uploaded to YouTube
  -cid YOUTUBE_CATEGORY_ID, --youtube_category_id YOUTUBE_CATEGORY_ID
                        Select the category id that should be assigned to your
                        podcast episode videos. Find list of available
                        categories here: https://developers.google.com/youtube
                        /v3/docs/videoCategories/list
  -t YOUTUBE_TAGS, --youtube_tags YOUTUBE_TAGS
                        Add tags to your podcast episode videos.(i.e. 'news,
                        arts, culture')             
```

## More Details
The video is created using the RSS feed. It takes the episode image and overlays the show logo on the top left corner. The video output is an mkv file. 

The program will not work without episode images. Your `<item>` should include an `<[itunes]:image>` 