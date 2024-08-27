from flask import Flask, request, jsonify, render_template
from tasks import download_as_mp3, download_as_mp4, download_playlist
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format = request.form['format']
    
    app.logger.info(f"Received request to download {url} in {format} format")
    
    try:
        if "playlist" in url:
            task = download_playlist.delay(url, format)
        elif format == 'mp3':
            task = download_as_mp3.delay(url)
        else:
            task = download_as_mp4.delay(url)
        
        app.logger.info(f"Task created with ID: {task.id}")
        return jsonify({'task_id': task.id}), 202
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)