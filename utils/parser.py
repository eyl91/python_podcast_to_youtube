import requests
import tempfile
import os
import xml.etree.ElementTree as ET

# from utils.youtube import identify_missing_episodes
class Parser:
    def __init__(self, params, **kwargs):  # Constructor
        self.params = params
        self.feed = self.params.podcast_feed

    def parse_feed(self):
        try:
            r = requests.get(self.feed)
            with tempfile.TemporaryFile() as fp:
                fp.write(r.content)
                fp.seek(0)
                tree = ET.parse(fp)
        except requests.exceptions.MissingSchema:
            tree = ET.parse(self.feed)

        root = tree.getroot()
        channel = root[0]
        print("SUCCESS: parse_feed")
        return channel

    # def check_new_episodes(item, podcast_playlist_id):
    #     old_episodes_list = identify_missing_episodes(podcast_playlist_id)
    #     if item.findall("title")[0].text not in old_episodes_list:
    #         print("NEW EPISODE: {}".format(item.findall("title")[0].text))
    #         print("SUCCESS: check_new_episodes")
    #         return True

    def get_episode_data(self, **kwargs):
        episode_data = {}
        for element in kwargs["episode_item"]:
            episode_data[
                element.tag.split("}")[1]
                if "http://www.itunes.com/" in element.tag
                else element.tag
            ] = (
                # attrib is used for elements without text - i.e., enclosure, image
                element.text.strip()
                if element.text
                else element.attrib
            )
        # TODO: Handle KeyError for feeds that don't have episode images.
        title = (
            episode_data["title"]
            if len(episode_data["title"]) < 70
            else (episode_data["title"][:67]) + "..."
        )

        video_dict = dict(
            title=title,
            full_title=episode_data["title"],
            description=episode_data["description"],
            pubdate=episode_data["pubDate"],
            audio_file=episode_data["enclosure"]["url"],
            image_file=episode_data["image"]["href"]
            if "href" in episode_data["image"]
            else episode_data["image"],
            show_logo=kwargs["show_logo"],
        )

        print("SUCCESS: get_episode_data")
        return video_dict
