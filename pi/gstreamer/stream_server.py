#!/usr/bin/env python3
# stream_server.py
# Phase 1 Flash server - serves live HDMI capture feed to phone browser via SSE
# GStreamer pipeline must be running and writing to latest.jpg before running this program

import os
import time
import threading
from flask import Flask, Response, render_template_string
import shutil
# os for file system operations
# time for sleeping
# threading for handling multiple connections simultaneously
# Specific Flask libraries
# shutil for file and directory operations beyond the basic os module (copying and moving)

app = Flask(__name__)

FRAME_PATH = '/home/ktran/hevs/tests/latest.jpg'

# Simple HTML page served to phone browser
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>HEVS Live View</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: black; display: flex; justify-content: center; align-items: center; height: 100vh; }
        img { width: 100%; max-width: 100%; height: auto; }
    </style>
</head>
<body>
    <img id="feed" src="/frame" />
    <script>
        function refreshFrame() {
            document.getElementById('feed').src = '/frame?t=' + Date.now();
        }
        setInterval(refreshFrame, 100);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
	return render_template_string(HTML)
# Defines what happens when the phone browser visits the rootURL, which renders the HTML string
# and sends it back to the browser

@app.route('/frame')
def frame():
	# Serve the latest captured frame as JPEG
	if not os.path.exists(FRAME_PATH):
		return Response(b'', mimetype='image/jpeg')
	# Copy to temp read buffer to avoid race condition
	try:
		tmp_path = FRAME_PATH + '.read'
		shutil.copy2(FRAME_PATH, tmp_path)
		with open(FRAME_PATH, 'rb') as f:
			data = f.read()
		return Response(data, mimetype='image/jpeg')
	except Exception:
		return Response(b'', mimetype='image/jpeg')
# Defines what happens when the browser requests /frame. First, it checks if the file exists,
# if not, returns a 404 error. If it does exist, it opens it in binary read mode, reads the bytes
# into data, then returns those bytes as an HTTP response with the MIME type set to image/jpeg so
# the browser knows that it's receiving an image. The browser renders those bytes directly as the
# camera frame. 

@app.route('/stream')
def stream():
	# SSE endpoint - pushes update event to browser when new frame is available
	def generate():
		last_modified = 0
		while True:
			try:
				modified = os.path.getmtime(FRAME_PATH)
				if modified > last_modified:
					last_modified = modified
					yield 'data: update\n\n'
			except FileNotFoundError:
				pass
			time.sleep(0.033) # ~30fps check rate
	return Response(generate(), mimetype='test/event-stream')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
