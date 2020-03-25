import os

# Google
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

scopes = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


def youtube_auth():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secrets.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes
    )
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials
    )
    print("SUCCESS: youtube_auth")
    return youtube


def youtube_upload(video_dict, podcast_playlist_id):
    youtube = youtube_auth()

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "categoryId": "22",
                "description": "{}\n{}".format(
                    video_dict["description"], video_dict["story_link"]
                ),
                "title": video_dict["title"],
            },
            "status": {"privacyStatus": "private"},
        },
        media_body=MediaFileUpload(
            video_dict["output_file"], chunksize=-1, resumable=True
        ),
    )
    response = request.execute()
    print("SUCCESS: youtube_upload: {}".format(response["id"]))
    os.remove(video_dict["output_file"])
    print("SUCCESS: output_file deleted")
    playlist_update(youtube, podcast_playlist_id, response["id"])


def playlist_update(youtube, podcast_playlist_id, video_id):
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": podcast_playlist_id,
                "position": 0,
                "resourceId": {"kind": "youtube#video", "videoId": video_id},
            }
        },
    )
    print("SUCCESS: playlist_update")
    response = request.execute()


def identify_missing_episodes(podcast_playlist_id):
    print("PODCAST PLAYLIST  ID", podcast_playlist_id)
    youtube = youtube_auth()
    request = youtube.playlistItems().list(
        part="snippet,contentDetails", maxResults=25, playlistId=podcast_playlist_id
    )
    response = request.execute()
    video_titles_list = []
    for video in response["items"]:
        video_titles_list.append(video["snippet"]["title"])
    print("SUCCESS: indetify_missing_episodes")
    return video_titles_list
