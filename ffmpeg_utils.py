# -*- coding: utf-8 -*-
from subprocess import Popen


class FFMPEG():
    def __init__(self):
        pass

    def screen_capture_recorder(self, times, w, h, x, y, save_path):
        print('开始录屏')
        Popen(
            'ffmpeg -y -t %s -f dshow -i video="screen-capture-recorder" -vf crop=w=%s:h=%s:x=%s:y=%s -qp 0 -preset ultrafast %s' % (
                times, x, y, w, h, save_path))
