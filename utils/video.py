import datetime
import os
import requests
import subprocess
from shutil import copyfile
import tempfile

from PIL import Image, ImageDraw, ImageFont


class Video:
    def __init__(video_dict, params):  # Constructor
        self.video_dict = video_dict
        self.params = params

    def make_ep_image(self):

        audio_ep_req = requests.get(self.video_dict["audio_file"])
        image_ep_req = requests.get(self.video_dict["image_file"])

        with tempfile.NamedTemporaryFile(
            suffix=".mp3"
        ) as audio_ep, tempfile.NamedTemporaryFile(suffix=".jpg") as image_ep:
            audio_ep.write(audio_ep_req.content)
            image_ep.write(image_ep_req.content)
            if self.params.logo:
                image_show_req = requests.get(self.video_dict["show_logo"])
                with tempfile.NamedTemporaryFile(suffix="jpg") as image_show:
                    image_show.write(image_show_req.content)
                    resize_image(image_ep=image_ep.name, show_logo=image_show.name)
            else:
                resize_image(image_ep=image_ep.name)

            self.video_dict.update(
                {"audio_file": audio_ep.name, "image_file": image_ep.name}
            )
            return make_video(video_dict)

    def make_default_ep_image(self):
        audio_ep_req = requests.get(self.video_dict["audio_file"])
        with tempfile.NamedTemporaryFile(
            suffix=".mp3"
        ) as audio_ep, tempfile.NamedTemporaryFile(suffix=".jpg") as image_ep:
            audio_ep.write(audio_ep_req.content)
            with open(self.params.default_image) as img_file:
                copyfile(img_file.name, image_ep.name)
                # TODO: Should I check for -ot here? if there's default image with text already in it. it should not be overlayed.

                add_info_text(self.video_dict, image_ep.name)

                self.video_dict.update(
                    {"audio_file": audio_ep.name, "image_file": image_ep.name}
                )

                return make_video(self.video_dict)

    def add_info_text(self, video_dict, image_ep_path):
        print(video_dict)
        # Main image resize
        image_bg = Image.open(image_ep_path)
        image_width = 1280
        wpercent = image_width / image_bg.size[0]
        hsize = int((image_bg.size[1] * wpercent))
        main_image = image_bg.resize((image_width, hsize), Image.LANCZOS)

        pubdate_datetime = datetime.datetime.strptime(
            video_dict["pubdate"], "%a, %d %b %Y %H:%M:%S %z"
        )

        # Add text
        # Add default font ImageFont.load_default()
        img = ImageDraw.Draw(main_image)
        font_title = ImageFont.truetype("../resources/fonts/title.ttf", 45)
        font_date = ImageFont.truetype("../resources/fonts/subtitle.ttf", 30)
        # Adding title with character limit per line
        starting_height = 325
        for line in parsed_title(video_dict["full_title"]):
            img.text((610, starting_height), line, font=font_title, fill="black")
            starting_height = starting_height + 50
        # Adding date under title
        img.text(
            (610, (starting_height + 25)),
            pubdate_datetime.strftime("%B %d, %Y"),
            font=font_date,
            fill="black",
        )
        # main_image.show()
        main_image.save(image_ep_path)

    def resize_image(self, **kwargs):
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

    def parsed_title(self, title):
        # charLimit specific for this font & size
        charLimit = 20
        title_list = [(t, len(t)) for t in title.split(" ")]
        lines = []
        line = ""
        counter = 0
        for t in title_list:
            if (counter + t[1]) <= charLimit:
                counter = counter + t[1]
                line = ((line + " ") + t[0]).strip()
                if title_list.index(t) == (len(title_list) - 1):
                    # Save completed line if it's the last word
                    lines.append(line)
                    # Reset line + counter
                    counter = 0
                    line = ""
            else:
                # Save completed line
                lines.append(line)
                # Start next line
                counter = t[1]
                line = (t[0]).strip()
                if title_list.index(t) == (len(title_list) - 1):
                    # Save completed line if it's the last word
                    lines.append(line)
                    # Reset line + counter
                    counter = 0
                    line = ""

        return lines

    def make_video(self, video_dict):
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

    def delete_tmp_video(self, output_file):
        os.remove(output_file)
