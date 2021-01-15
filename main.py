import argparse
from utils.parser import get_episode_data, parse_feed
from utils.video import make_ep_image, make_default_ep_image, delete_tmp_video
from utils.youtube import youtube_upload


def main(args):
    print(args)
    feed = parse_feed(args.podcast_feed)
    episodes = []
    show_logo = ""
    output_files = []

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
            if args.specific_episode:
                title = item.find("title").text
                for selected_title in args.specific_episode:
                    if selected_title.lower() == title.lower().strip():
                        episodes.append(item)
            else:
                episodes.append(item)

    if args.latest:
        episodes = episodes[: (args.latest)]

    for episode_item in episodes:
        video_dict = (
            make_ep_image(
                get_episode_data(episode_item=episode_item, show_logo=show_logo), args,
            )
            if not args.default_image
            else make_default_ep_image(
                get_episode_data(episode_item=episode_item, show_logo=show_logo),
                args.default_image,
            )
        )
        if args.local_file:
            output_files.append(video_dict["output_file"])
            print("Local file: ", output_files)
        else:
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
        help="Arg should be a link to the feed (i.e., https://feeds.kpbs.org/cinema-junkie) or path to an xml file",
    )
    parser.add_argument(
        "-cid",
        "--youtube_category_id",
        help="Select the category id that should be assigned to your podcast episode videos. Find list of available categories here: https://developers.google.com/youtube/v3/docs/videoCategories/list",
        default="22",
    )
    parser.add_argument(
        "-d",
        "--default_image",
        help="Set path for default image to be used for episodes.",
    )
    parser.add_argument(
        "-la",
        "--latest",
        help="Specify how many of the latest episodes (top being the latest) should be uploaded to YouTube. Otherwise it will parse all episodes.",
        type=int,
    )
    parser.add_argument(
        "-lf",
        "--local_file",
        help="Videos won't be uploaded to YouTube. It will be saved locally.",
        action="store_true",
    )
    parser.add_argument(
        "-lo",
        "--logo",
        help="Add if the podcast logo should be added over the episode image.",
        action="store_true",
    )
    # parser.add_argument(
    #     "-nc",
    #     "--no_old_episodes_check",
    #     help="Confirm upload of existing video on YouTube.",
    #     action="store_true",
    # )
    parser.add_argument(
        "-ot",
        "--overlay_text_episode_info",
        help="Text with episode information (Show Title, Episode Title, Publication Date) to be overlayed on the image",
        action="store_true",
    )
    parser.add_argument(
        "-p",
        "--youtube_private",
        help="Add if the podcast epsiodes uploaded to YouTube should be set to private",
        action="store_true",
    )
    parser.add_argument(
        "-pid",
        "--podcast_youtube_playlist_id",
        help="Arg should be the YouTube playlist ID this video will be set to, it's also necessary to check what episodes in the feed have already been uploaded to YouTube",
    )
    parser.add_argument(
        "-sep",
        "--specific_episode",
        nargs="+",
        type=str,
        help="Pass specific episode title(s) to be uploaded to YouTube",
    )
    parser.add_argument(
        "-t",
        "--youtube_tags",
        help="Add tags to your podcast episode videos.(i.e. 'news, arts, culture')",
        default=[],
    )
    parser.add_argument(
        "-u",
        "--youtube_unlisted",
        help="Add if the podcast epsiodes uploaded to YouTube should be set to unlisted",
        action="store_true",
    )

    args = parser.parse_args()
    if not args.default_image and args.overlay_text_episode_info:
        parser.error(
            "--overlay_text_episode_info can only be set when --default_image is set."
        )
    if args.default_image and args.logo:
        parser.error("--logo can only be set when --default_image is NOT set.")
    if args.latest and args.specific_episode:
        parser.error("--latest can only be set when --specific_episode is NOT set.")
    if args.youtube_private and args.youtube_unlisted:
        parser.error(
            "--youtube_private can only be set when --youtube_unlisted is NOT set."
        )
    main(args)
