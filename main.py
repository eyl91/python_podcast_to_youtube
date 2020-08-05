import argparse
from parser import get_episode_data, parse_feed, check_new_episodes
from video import download_mp3, delete_tmp_video
from youtube import youtube_upload


def main(args):
    print(args)
    feed = parse_feed(args.podcast_feed)
    episodes = []
    show_logo = ""

    for item in feed:
        if args.logo and "image" in item.tag:
            try:
                show_logo = item.attrib["href"]
            except KeyError as e:
                for child in item:
                    if "url" in child.tag:
                        show_logo = child.text
                        break

        if item.tag == "item":
            episodes.append(item)
    if args.latest:
        episodes = episodes[: (args.latest)]
    for episode_item in episodes:
        video_dict = download_mp3(
            get_episode_data(episode_item=episode_item, show_logo=show_logo), args,
        )
        youtube_upload(
            video_dict=video_dict,
            playlist_id=args.podcast_youtube_playlist_id,
            category=args.youtube_category_id,
            tags=args.youtube_tags,
            private=args.youtube_private,
            unlisted=args.youtube_unlisted,
        )
        delete_tmp_video(video_dict["output_file"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "podcast_feed",
        help="Arg should be the link to the feed (i.e., https://feeds.kpbs.org/cinema-junkie) or a local xml file",
    )
    parser.add_argument(
        "-la",
        "--latest",
        help="Specify how many of the latest episodes (top being the latest) should be uploaded to YouTube. Otherwise it will parse all episodes.",
        type=int,
    )
    parser.add_argument(
        "-nc",
        "--no_old_episodes_check",
        help="Confirm upload of existing video on YouTube.",
        action="store_true",
    )
    parser.add_argument(
        "-lo",
        "--logo",
        help="Add if the podcast logo should be added over the episode image.",
        action="store_true",
    )
    parser.add_argument(
        "-p",
        "--youtube_private",
        help="Add if the podcast epsiodes uploaded to YouTube should be set to private",
        action="store_true",
    )
    parser.add_argument(
        "-u",
        "--youtube_unlisted",
        help="Add if the podcast epsiodes uploaded to YouTube should be set to unlisted",
        action="store_true",
    )
    parser.add_argument(
        "-pid",
        "--podcast_youtube_playlist_id",
        help="Arg should be the YouTube playlist ID this video will be set to, it's also necessary to check what episodes in the feed have already been uploaded to YouTube",
    )
    parser.add_argument(
        "-cid",
        "--youtube_category_id",
        help="Select the category id that should be assigned to your podcast episode videos. Find list of available categories here: https://developers.google.com/youtube/v3/docs/videoCategories/list",
        default="22",
    )
    parser.add_argument(
        "-t",
        "--youtube_tags",
        help="Add tags to your podcast episode videos.",
        default=[],
    )

    args = parser.parse_args()
    main(args)
