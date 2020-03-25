import argparse
from parser import get_episode_data, parse_feed, check_new_episodes
from video import download_mp3
from youtube import youtube_upload


def main(podcast_feed, podcast_playlist_id):
    feed = parse_feed(podcast_feed)
    for item in feed:
        if "image" in item.tag:
            image_show = item.attrib["href"]
        if item.tag == "item":
            if check_new_episodes(item, podcast_playlist_id):
                video_dict = download_mp3(get_episode_data(item), image_show)
                youtube_upload(video_dict, podcast_playlist_id)
            else:
                print("OLD EPISODE: {}".format(item.findall("title")[0].text))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "podcast_feed",
        help="Arg should be the link to the feed (i.e., https://feeds.kpbs.org/cinema-junkie) - depending on the feed",
    )
    parser.add_argument(
        "podcast_playlist_id",
        help="Arg should be the YouTube playlist ID this video will be set to, it's also necessary to check what episodes in the feed have already been uploaded to YouTube",
    )

    args = parser.parse_args()
    main(args.podcast_feed, args.podcast_playlist_id)
