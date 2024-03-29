# -*- coding: utf-8 -*-
# http://adbshell.com/commands
# https://zhuanlan.zhihu.com/p/43731848
import base64
import os
import random
import re
import subprocess
import time

# https://pypi.org/project/delegator.py/
import delegator
# https://pypi.org/project/loguru/
from loguru import logger

from .find_image import search_img


def popen(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    popen.wait()
    lines = popen.stdout.readlines()
    return [line.decode('gbk') for line in lines]


def phone_screen_if_exist_image(dName, image_name, confidencevalue=0.7, wait=3, del_shot_image=True):
    # 判断是否存在某个图片特征
    adb = ADButil(dName)

    if wait > 0:
        start_time = time.time()
        while start_time + wait > time.time():
            screen_image_path = adb.screenshot()

            pos = search_img(screen_image_path, image_name, confidencevalue)
            if del_shot_image:
                os.remove(screen_image_path)
            if pos[0] != -1 and pos[1] != -1:
                break
            time.sleep(1)
    else:
        screen_image_path = adb.screenshot()

        pos = search_img(screen_image_path, image_name, confidencevalue)

    print(pos)
    if pos[0] != -1 and pos[1] != -1:
        return True
    else:
        return False


def screen_image_click(dName, image_name, confidencevalue=0.7, wait=3, del_shot_image=True):
    adb = ADButil(dName)
    # pos = search_img(screen_image_path, image_name, confidencevalue)
    # if pos[0] != -1 and pos[1] != -1:
    #     adb.click(pos[0], pos[1])
    #     return pos

    if wait > 0:
        start_time = time.time()
        while start_time + wait > time.time():
            screen_image_path = adb.screenshot()

            pos = search_img(screen_image_path, image_name, confidencevalue)
            if del_shot_image:
                try:
                    os.remove(screen_image_path)
                except:
                    pass
            if pos[0] != -1 and pos[1] != -1:
                break
            time.sleep(1)
    else:
        screen_image_path = adb.screenshot()

        pos = search_img(screen_image_path, image_name, confidencevalue)
    adb.click(pos[0], pos[1])
    return pos


class ADButil(object):
    # https://blog.csdn.net/jlminghui/article/details/39268419
    def __init__(self, dname='', dname_list=[]):
        self.dname = dname  # 当前设备

        self.dname_list = dname_list  # 设备列表
        # self.getDevicesAll()
        ret = os_system('adb -s %s -d shell getprop ro.product.brand' % (self.dname))
        if ret.err !='':
            logger.error('设备连接失败')
            self.error = 1
        else:
            self.error = 0

    def page_refresh(self):
        self.swipe(toup=False, height=600)
        time.sleep(5)

    def swipe(self, height=200, times=1, toup=True):
        for r in range(0, times):
            x = random.randint(350, 850)
            y1 = random.randint(1000, 1050)
            y2 = y1 - random.randint(height, height + 50)
            if toup:
                os_system(
                    "adb -s " + self.dname + " shell input swipe %d %d %d %d 1500 &" % (x, y1, x, y2))  # 后台执行 小米800-200
            else:
                os_system(
                    "adb -s " + self.dname + " shell input swipe %d %d %d %d 1500 &" % (x, y2, x, y1))  # 后台执行 小米800-200
            time.sleep(1)

    def startup_app_by_image(self, image_path, wait=7):
        print('启动应用')
        self.goto_home(4)
        screen_image_click(self.dname, image_path,0.5)
        # 等待
        time.sleep(wait)

    def startup_app(self, startup_path, wait=7):
        # >adb shell dumpsys window windows | grep mCurrent
        print('启动应用：' + startup_path)
        os_system("adb -s %s shell am start -n %s" % (self.dname, startup_path))
        time.sleep(wait)

    def kill_app(self, packname, wait=1):
        time.sleep(wait)
        print('关闭应用：' + packname)
        os_system("adb -s %s shell am force-stop %s" % (self.dname, packname))

    def put_mute(self):
        # 话筒静音键
        # 91
        # KEYCODE_VOLUME_MUTE
        # 扬声器静音键
        # 164
        # https://www.cnblogs.com/zhuminghui/p/10470865.html
        self.input_keyevent(164)
        self.input_keyevent(91)
        for r in range(0, 10):
            os_system("adb -s %s shell input keyevent 25" % self.dname)

    def switch_wifi(self, enable=True):
        if enable:
            enable = 'enable'
        else:
            enable = 'disable'

        os_system("adb -s %s shell svc wifi %s" % (self.dname, enable))

    def put_screen_brightness(self, value=15):
        print('调整屏幕亮度:' + str(value))
        os_system("adb -s %s shell settings put system screen_brightness %s" % (self.dname, value))

    # 获取屏幕分辨率
    def getDevicesScreenWH(self):
        screenWH = []

        # 获取分辨率
        # 获取屏幕分辨率计算屏幕中心
        f = os.popen("adb -s " + self.dname + " shell wm size")
        screen_width, screen_height = re.search("(\d{3,4})x(\d{3,4})", f.read()).groups()
        center = (int(screen_width) / 2, int(screen_height) / 2)
        # screenWH.append([int(screen_width), int(screen_height)])
        print('屏幕宽高：%sx%s' % (screen_width, screen_height))
        return (int(screen_width), int(screen_height))

    def getDevicesAll(self):
        # 获取所有设备
        devices_list = []
        try:
            for dName_ in os.popen("adb devices"):
                if "\t" in dName_:
                    # 真机
                    pname = dName_.split("\t")[0]
                    print('设备名称：' + pname)
                    os_system('adb -s %s -d shell getprop ro.product.brand' % (pname))
                    os_system('adb -s %s -d shell getprop ro.product.model' % (pname))
                    devices_list.append(pname)
                    # 模拟器检索
                    # findres = dName_.find("emulator")
                    # if findres != -1:
                    #     devices.append(dName_.split("\t")[0])
            # devices_list.sort(cmp=None, key=None, reverse=False)
        except Exception as e:
            print(e)
        print("\n设备名称: %s \n总数量:%s台" % (devices_list, len(devices_list)))
        return devices_list

    def goto_home(self, times=1):
        print('返回主页')
        for r in range(0, times):
            self.input_keyevent(3)  # 返回主页

    def show_screen(self):

        mScreenOn = re.search('mScreenOn=true', os.popen('adb -s %s shell dumpsys power' % (self.dname)).read())
        print(mScreenOn)
        if mScreenOn == None:
            print('锁屏状态')
            self.input_keyevent(26)
        else:
            print('非锁屏状态')

    def send_file(self, src_file_path, dest_dir='/sdcard/DCIM/Camera'):
        os_system('adb -s %s push %s %s' % (self.dname, src_file_path, dest_dir))
        os_system('adb -s %s shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file:///%s/%s' % (
            self.dname, dest_dir, os.path.basename(src_file_path)))

    def goback(self, times=1):
        print('返回')
        for r in range(0, times):
            self.input_keyevent(4)  # 返回主页
            time.sleep(1)

    def input_keyevent(self, keycode):
        # https://www.jianshu.com/p/bfc978d52e76
        print('发送keycode:%s' % (keycode))

        os_system('adb -s %s shell input keyevent "%s"' % (self.dname, keycode))

    def input_text(self, text, zh_cn=False):
        time.sleep(2)

        # 安装apk adb install ADBKeyBoard.apk
        """其它的指令
            输入中文文本
            adb shell am broadcast -a ADB_INPUT_TEXT --es msg '上海-悠悠'
    
            发送 keyevent 事件 (67 = KEYCODE_DEL)
            adb shell am broadcast -a ADB_INPUT_CODE --ei code 67
    
            发送编辑器动作 (2 = IME_ACTION_GO)
            adb shell am broadcast -a ADB_EDITOR_CODE --ei code 2
    
            发送Unicode字符，To send 😸 Cat
            adb shell am broadcast -a ADB_INPUT_CHARS --eia chars '128568,32,67,97,116'"""

        if zh_cn:
            text = base64.b64encode(text.encode('utf-8')).decode("utf-8")
            print('发送文本：' + text)
            os_system('adb -s %s  shell ime set com.android.adbkeyboard/.AdbIME' % (self.dname))
            os_system('adb -s %s  shell ime set com.android.adbkeyboard/.AdbIME' % (self.dname))
            time.sleep(2)
            os_system('adb  -s %s shell am broadcast -a ADB_INPUT_B64 --es msg "%s"' % (
                self.dname, text))
            os_system('adb -s %s  shell am broadcast -a ADB_EDITOR_CODE --ei code 4' % (self.dname))
            # os_system('adb -s %s shell input text "%s"' % (self.dname, text))  # 无法输入中文
            # 还原输入法
            # 查看输入法 adb shell ime list -s
            time.sleep(2)
            # os_system('adb -s %s  shell ime set com.baidu.input_huawei/.ImeService' % (self.dname))
            # time.sleep(3)
        else:
            print('发送文本：' + text)

            os_system('adb -s %s  shell input text "%s"' % (self.dname, text))

    def change_ime(self, adb=True):
        if adb:

            os_system('adb -s %s  shell ime set com.android.adbkeyboard/.AdbIME' % (self.dname))
        else:

            os_system('adb -s %s  shell ime set com.baidu.input_huawei/.ImeService' % (self.dname))

    def click(self, x, y):
        print('点击：(%s,%s)' % (x, y), self.dname)
        if x == -1 and y == -1:
            return False
        os_system("adb -s %s shell input tap %d %d" % (self.dname, x, y))
        # time.sleep(2)

    def screenshot(self, file_name='screen_' + str(int(time.time())) + '.jpg',
                   save_path=os.path.abspath('./Screenshots'), del_shot_image=True):
        # cmd adb shell screencap -p /sdcard/screen.jpg && adb pull /sdcard/screen.jpg
        print('截图' + self.dname)
        try:
            os.mkdir('./Screenshots')
        except:
            pass
        os_system("adb -s %s shell screencap -p /sdcard/Pictures/Screenshots/%s" % (self.dname, file_name))
        # 推送 到当前目录下
        os_system("adb -s %s pull /sdcard/Pictures/Screenshots/%s %s" % (self.dname, file_name, save_path))
        if del_shot_image:
            os_system('adb -s %s shell rm -f /sdcard/Pictures/Screenshots/%s' % (self.dname, file_name))
        return save_path + '/' + file_name


def os_system(cmd):
    logger.debug(cmd)
    ret = delegator.run(cmd, timeout=60)
    logger.debug(ret.out+ret.err)

    return ret
