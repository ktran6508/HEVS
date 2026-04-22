#!/usr/bin/env python3
# frame_watcher.py
# Watches for new frames from GStreamer and atomically renames to latest.jpg
# Eliminates race condition between GStreamer write and Flask read

import os
import time
import shutil

TMP_PATH = '/home/ktran/hevs/tests/frame_tmp.jpg'
FINAL_PATH = '/home/ktran/hevs/tests/latest.jpg'

last_modified = 0

while True:
    try:
        modified = os.path.getmtime(TMP_PATH)
        if modified > last_modified:
            last_modified = modified
            # os.rename is atomic on Linux — no partial reads possible
            os.rename(TMP_PATH, FINAL_PATH)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f'Error: {e}')
    time.sleep(0.01)
