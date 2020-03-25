import requests
import subprocess
import tempfile
from PIL import Image


def download_mp3(video_dict, image_show):
    image_show_req = requests.get(image_show)
    audio_req = requests.get(video_dict["audio_file"])
    image_req = requests.get(video_dict["image_file"])

    with tempfile.NamedTemporaryFile(
        suffix=".mp3"
    ) as audio, tempfile.NamedTemporaryFile(
        suffix=".jpg"
    ) as image, tempfile.NamedTemporaryFile(
        suffix=".jpg"
    ) as image_show:
        audio.write(audio_req.content)
        image.write(image_req.content)
        image_show.write(image_show_req.content)
        resize_image(image.name, image_show.name)
        video_dict.update({"audio_file": audio.name, "image_file": image.name})
        return make_video(video_dict)


def resize_image(image, image_show):
    image_bg = Image.open(image).convert("RGBA")
    image_fg = Image.open(image_show).resize((200, 200)).convert("RGBA")
    image_bg.paste(image_fg, (25, 25), image_fg)

    image_width = 700
    wpercent = image_width / float(image_bg.size[0])
    hsize = int((float(image_bg.size[1]) * float(wpercent)))
    final_image = image_bg.resize((image_width, hsize), Image.BICUBIC)
    final_image.convert("RGB").save(image)


def make_video(video_dict):
    output_file = "/tmp/{}.mkv".format("_".join(video_dict["title"].split()))
    subprocess.run(
        [
            "ffmpeg",
            "-loop",
            "1",
            "-framerate",
            "2",
            "-i",
            video_dict["image_file"],
            "-i",
            video_dict["audio_file"],
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-tune",
            "stillimage",
            "-crf",
            "18",
            "-c:a",
            "copy",
            "-shortest",
            "-movflags",
            "+faststart",
            "-vf",
            "pad='width=ceil(iw/2)*2:height=ceil(ih/2)*2'",
            output_file,
        ]
    )
    return {
        "title": video_dict["title"],
        "description": video_dict["description"],
        "story_link": video_dict["story_link"],
        "output_file": output_file,
    }
