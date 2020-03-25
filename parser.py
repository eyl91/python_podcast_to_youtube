import xml.etree.ElementTree as ET
from youtube import identify_missing_episodes


def parse_feed(feed):
    tree = ET.parse(feed)
    root = tree.getroot()
    channel = root[0]
    print("SUCCESS: parse_feed")
    return channel


def check_new_episodes(item, podcast_playlist_id):
    old_episodes_list = identify_missing_episodes(podcast_playlist_id)
    if item.findall("title")[0].text not in old_episodes_list:
        print("NEW EPISODE: {}".format(item.findall("title")[0].text))
        print("SUCCESS: check_new_episodes")
        return True


def get_episode_data(item):
    episode_data = {}
    for element in item:
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

    print("SUCCESS: get_episode_data")
    return {
        "title": episode_data["title"],
        "description": episode_data["description"],
        "story_link": episode_data["link"],
        "audio_file": episode_data["enclosure"]["url"],
        "image_file": episode_data["image"]["href"],
    }
