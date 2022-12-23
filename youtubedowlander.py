"

Author: Yumaka
Scope: FFMPEG

"

# meta developer: @lukaszmods :3

import os
import subprocess

from pytube import YouTube
from telethon.tl.types import Message

from .. import loader, utils


@loader.tds
class YouTubeMod(loader.Module):
    """Скачать видео с ютуба"""

    strings = {
        "name": "YouTube",
        "args": "🎞 <code>You need to specify link!</code>",
        "downloading": "🎞 <code>Downloading...</code>",
        "not_found": "🎞 <b><u>Video not found...</u></b>",
    }

    strings_ru = {
        "args": "🎞 <code>Ты должен указать ссылку на видео!</code>",
        "downloading": "🎞 <code>Скачиваю...</code>",
        "not_found": "🎞 <b><u>Такого видео не найдено!</u></b>",
        "_cmd_doc_yt": "[mp3] <ссылка> - Скачать видео YouTube",
        "_cls_doc": "Скачать YouTube видео",
    }

    @loader.unrestricted
    async def ytcmd(self, message: Message):
        """[mp3] <link> - Download video from youtube"""
        args = utils.get_args_raw(message)
        message = await utils.answer(message, self.strings("downloading"))

        ext = False
        if len(args.split()) > 1:
            ext, args = args.split(maxsplit=1)

        if not args:
            return await utils.answer(message, self.strings("args"))

        def dlyt(videourl, path):
            yt = YouTube(videourl)
            yt = (
                yt.streams.filter(progressive=True, file_extension="mp4")
                .order_by("resolution")
                .desc()
                .first()
            )
            return yt.download(path)

        def convert_video_to_audio_ffmpeg(video_file, output_ext="mp3"):
            filename, ext = os.path.splitext(video_file)
            out = f"{filename}.{output_ext}"
            subprocess.call(
                ["ffmpeg", "-y", "-i", video_file, out],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            os.remove(video_file)
            return out

        path = "/tmp"
        try:
            path = await utils.run_sync(dlyt, args, path)
        except Exception:
            await utils.answer(message, self.strings("not_found"))
            return

        if ext == "mp3":
            path = convert_video_to_audio_ffmpeg(path)

        await self._client.send_file(message.peer_id, path)
        os.remove(path)

        if message.out:
            await message.delete()
