import os
import requests
import subprocess
import tempfile
from PIL import Image


def download_mp3(video_dict, args):

    audio_ep_req = requests.get(video_dict["audio_file"])
    image_ep_req = requests.get(video_dict["image_file"])

    with tempfile.NamedTemporaryFile(
        suffix=".mp3"
    ) as audio_ep, tempfile.NamedTemporaryFile(suffix=".jpg") as image_ep:
        audio_ep.write(audio_ep_req.content)
        image_ep.write(image_ep_req.content)
        if args.logo:
            image_show_req = requests.get(video_dict["show_logo"])
            with tempfile.NamedTemporaryFile(suffix="jpg") as image_show:
                image_show.write(image_show_req.content)
                resize_image(image_ep=image_ep.name, show_logo=image_show.name)
        else:
            resize_image(image_ep=image_ep.name)

        video_dict.update({"audio_file": audio_ep.name, "image_file": image_ep.name})
        return make_video(video_dict)


def resize_image(**kwargs):
    # Logo resize
    if "show_logo" in kwargs:
        logo_image = Image.open(kwargs["show_logo"])
        logo_maxsize = (300, 300)
        logo_image.thumbnail(logo_maxsize, Image.LANCZOS)
        logo_image = logo_image.convert("RGBA")

    # Main image resize
    image_bg = Image.open(kwargs["image_ep"])
    image_width = 1280
    wpercent = image_width / image_bg.size[0]
    hsize = int((image_bg.size[1] * wpercent))
    final_image = image_bg.resize((image_width, hsize), Image.LANCZOS)
    # add logo if it exists
    if "show_logo" in kwargs:
        final_image = final_image.convert("RGBA")
        final_image.paste(logo_image, (25, 25), logo_image)
        final_image = final_image.convert("RGB")
    final_image.save(kwargs["image_ep"])


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
        "output_file": output_file,
    }


def delete_tmp_video(output_file):
    os.remove(output_file)
