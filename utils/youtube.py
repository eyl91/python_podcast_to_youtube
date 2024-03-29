import http.client
import httplib2
import os
import random
import time
import settings
import sys

# Google
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

scopes = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (
    httplib2.HttpLib2Error,
    IOError,
    http.client.NotConnected,
    http.client.IncompleteRead,
    http.client.ImproperConnectionState,
    http.client.CannotSendRequest,
    http.client.CannotSendHeader,
    http.client.ResponseNotReady,
    http.client.BadStatusLine,
)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]


class YouTube:
    def __init__(self, **kwargs):  # Constructor
        self.video_dict = kwargs["video_dict"]
        self.playlist_id = kwargs["playlist_id"]
        self.category = kwargs["category"]
        self.tags = kwargs["tags"]
        self.private = kwargs["private"]
        self.unlisted = kwargs["unlisted"]

    def youtube_auth(self):
        print(settings.REFRESH_TOKEN)
        creds = Credentials(
            token=None,
            refresh_token=settings.REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
        )

        api_service_name = "youtube"
        api_version = "v3"

        try:
            youtube = build(
                api_service_name, api_version, credentials=creds, cache_discovery=False
            )
            return youtube
        except RefreshError as e:
            print(e)
            sys.exit(-1)

    def youtube_upload(self):
        youtube = self.youtube_auth()
        insert_request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "categoryId": self.category,
                    "description": f"{self.video_dict['description']}",
                    "tags": self.tags,
                    "title": self.video_dict[
                        "title"
                    ],  # TODO: Add name of podcast here? i.e. Port of Entry Podcast: <title>
                },
                "status": {
                    "privacyStatus": "private"
                    if self.private
                    else "unlisted"
                    if self.unlisted
                    else "public"
                },
            },
            media_body=MediaFileUpload(
                self.video_dict["output_file"], chunksize=-1, resumable=True
            ),
        )

        video_id = self.resumable_upload(insert_request)
        if self.playlist_id:
            self.playlist_update(youtube, video_id)

    def resumable_upload(self, insert_request):
        response = None
        error = None
        retry = 0
        while response is None:
            try:
                print("Uploading file...")
                status, response = insert_request.next_chunk()
                if response is not None:
                    if "id" in response:
                        print(f"Video id {response['id']} was successfully uploaded.")
                        return response["id"]
                    else:
                        exit(
                            f"The upload failed with an unexpected response: {response}"
                        )
            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = (
                        f"A retriable HTTP error {e.resp.status} occurred:{e.content}"
                    )
                else:
                    raise
            except RETRIABLE_EXCEPTIONS as e:
                error = f"A retriable error occurred: {e}"

            if error is not None:
                print(error)
                retry += 1
                if retry > MAX_RETRIES:
                    exit("No longer attempting to retry.")

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print(f"Sleeping {sleep_seconds} seconds and then retrying...")
                time.sleep(sleep_seconds)

    def playlist_update(self, youtube, video_id):
        request = youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": self.playlist_id,
                    # "position": 0,  TODO: If the playlist uses auto sorting, this won't work. Remove this? Account for auto sorting?
                    "resourceId": {"kind": "youtube#video", "videoId": video_id},
                }
            },
        )
        response = request.execute()
        print("SUCCESS: playlist_update")

    # def identify_missing_episodes(podcast_playlist_id):
    #     youtube = youtube_auth()
    #     request = youtube.playlistItems().list(
    #         part="snippet,contentDetails", maxResults=25, playlistId=podcast_playlist_id
    #     )
    #     response = request.execute()
    #     video_titles_list = []
    #     for video in response["items"]:
    #         video_titles_list.append(video["snippet"]["title"])
    #     return video_titles_list
