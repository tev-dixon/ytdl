## Install
```bash
pip install flask gevent celery redis pytube moviepy
```

```bash
sudo apt update
sudo apt install redis-server ffmpeg

```

## Start Server
```bash
celery -A tasks worker --loglevel=info
```

## Run App
```bash
python app.py
```