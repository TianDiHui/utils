# -*- coding: utf-8 -*-
import time
from utils.find_image import search_img

import pyautogui


class WinScreen(object):

    def __init__(self):
        self.screenWidth, self.screenHeight = pyautogui.size()

    # 截屏
    def shots(self, x=0, y=0, w=pyautogui.size()[0], h=pyautogui.size()[1],
              file_path='./Screenshots/win_screenshot_' + str(int(time.time())) + '.jpg'):
        img = pyautogui.screenshot(region=(x, y, w, h))  # x,y,w,h
        img.save(file_path)
        return file_path
        # img = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

    # 找色
    def pos_by_image(self, image_path):
        screen_image_path = self.shots()
        pos = search_img(screen_image_path, image_path)
        pyautogui.click(pos[0], pos[1])
