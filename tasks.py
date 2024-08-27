from celery import Celery
from pytube import Playlist, YouTube
from moviepy.editor import AudioFileClip, VideoFileClip
import os
import logging

app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
logging.basicConfig(level=logging.DEBUG)

def download_video(video, prefix, output_path, format):
    try:
        title = video.title
        safe_title = ''.join([c for c in title if c.isalnum() or c in [' ', '-']]).rstrip()
        filename = f"{prefix}{safe_title}.{format}"
        
        logging.info(f"Downloading {title} in {format} format")
        
        if format == 'mp3':
            stream = video.streams.filter(only_audio=True).first()
        else:
            stream = video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        temp_path = stream.download(output_path=output_path, filename=f"{prefix}temp_video.mp4")
        
        if format == 'mp3':
            logging.info(f'Converting {title} to mp3...')
            clip = AudioFileClip(temp_path)
            clip.write_audiofile(os.path.join(output_path, filename), codec='mp3')
            clip.close()
        else:
            logging.info(f'Converting {title} to mp4...')
            os.rename(temp_path, os.path.join(output_path, filename))
        
        if format == 'mp3':
            os.remove(temp_path)
        
        logging.info(f"Successfully downloaded and converted {title}")
    except Exception as e:
        logging.error(f"Error downloading {title}: {str(e)}")
        raise

@app.task
def download_playlist(url, format):
    try:
        pl = Playlist(url)
        output_path = './downloads'
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        for i, video in enumerate(pl.videos, start=1):
            prefix = f"{str(i).zfill(2)} - "
            download_video(video, prefix, output_path, format)
        return {'status': 'Completed', 'message': f'Playlist downloaded and converted to {format}'}
    except Exception as e:
        logging.error(f"Error downloading playlist: {str(e)}")
        raise

@app.task
def download_as_mp3(url):
    return download_single(url, 'mp3')

@app.task
def download_as_mp4(url):
    return download_single(url, 'mp4')

def download_single(url, format):
    try:
        logging.info(f'Downloading single video as {format}...')
        yt = YouTube(url)
        prefix = ""
        output_path = './downloads'
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        download_video(yt, prefix, output_path, format)
        return {'status': 'Completed', 'filename': f'{yt.title}.{format}'}
    except Exception as e:
        logging.error(f"Error downloading single video: {str(e)}")
        raise