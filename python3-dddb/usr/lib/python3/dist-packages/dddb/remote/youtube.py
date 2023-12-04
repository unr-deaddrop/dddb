import yt_dlp
def download(URL: str, Path: str):
    dl_opts = {
        'outtmpl': Path,
    }
    with yt_dlp.YoutubeDL(dl_opts) as ydl:
        ydl.download([URL])
