# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
import base64
import os
import re
import time


class ADButil(object):
    # https://blog.csdn.net/jlminghui/article/details/39268419
    def __init__(self, dname='', dname_list=[]):
        self.dname = dname  # 当前设备
        self.dname_list = dname_list  # 设备列表

    def put_mute(self, value):
        # 话筒静音键
        # 91
        # KEYCODE_VOLUME_MUTE
        # 扬声器静音键
        # 164
        self.input_keyevent(164)
        self.input_keyevent(91)

    def put_screen_brightness(self, value):
        # 调整屏幕亮度
        os.system("adb -s %s shell settings put system screen_brightness %s" % (self.dname, value))

    # 获取屏幕分辨率
    def getDevicesScreenWH(self):
        screenWH = []

        # 获取分辨率
        # 获取屏幕分辨率计算屏幕中心
        f = os.popen("adb -s " + self.dName + " shell wm size")
        screen_width, screen_height = re.search("(\d{3,4})x(\d{3,4})", f.read()).groups()
        center = (int(screen_width) / 2, int(screen_height) / 2)
        screenWH.append([int(screen_width), int(screen_height)])
        return screenWH

    def getDevicesAll(self):
        # 获取所有设备
        devices_list = []
        try:
            for dName_ in os.popen("adb devices"):
                if "\t" in dName_:
                    # 真机
                    devices_list.append(dName_.split("\t")[0])
                    # 模拟器检索
                    # findres = dName_.find("emulator")
                    # if findres != -1:
                    #     devices.append(dName_.split("\t")[0])
            devices_list.sort(cmp=None, key=None, reverse=False)
        except Exception as e:
            print(e)
        print("\n设备名称: %s \n总数量:%s台" % (devices_list, len(devices_list)))
        return devices_list

    def goto_home(self):
        print('返回主页')
        self.input_keyevent(3)  # 返回主页
        self.input_keyevent(3)  # 返回主页
        self.input_keyevent(3)  # 返回主页
        self.input_keyevent(3)  # 返回主页
        self.input_keyevent(3)  # 返回主页

    def goback(self):
        print('返回')
        self.input_keyevent(4)  # 返回主页

    def input_keyevent(self, keycode):
        # https://www.jianshu.com/p/bfc978d52e76
        print('发送keycode:%s' % (keycode))

        os.system('adb -s %s shell input keyevent "%s"' % (self.dname, keycode))

    def input_text(self, text):
        print('发送文本：' + text)
        # 默认输入法设置：adb shell ime set com.android.adbkeyboard/.AdbIME
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

        # adb shell am broadcast -a ADB_INPUT_B64 --es msg "aGVsbG8s5L2g5aW977yM"
        os.system('adb  -s %s shell am broadcast -a ADB_INPUT_B64 --es msg "%s"' % (
            self.dname, base64.b64encode(text.encode('utf-8')).decode("utf-8")))
        time.sleep(2)
        os.system('adb -s %s  shell am broadcast -a ADB_EDITOR_CODE --ei code 4' % (self.dname))
        # os.system('adb -s %s shell input text "%s"' % (self.dname, text))  # 无法输入中文

    def click(self, x, y):
        print('点击：(%s,%s)' % (x, y), self.dname)
        if x == -1 and y == -1:
            return False
        os.system("adb -s %s shell input tap %d %d" % (self.dname, x, y))
        # time.sleep(2)

    def screenshot(self, file_name='screen_' + str(int(time.time())) + '.jpg',
                   save_path=os.path.abspath('./Screenshots')):
        # cmd adb shell screencap -p /sdcard/screen.jpg && adb pull /sdcard/screen.jpg
        print('截图' + self.dname)
        try:
            os.mkdir('./Screenshots')
        except:
            pass
        os.system("adb -s %s shell screencap -p /sdcard/Pictures/Screenshots/%s" % (self.dname, file_name))
        # 推送 到当前目录下
        os.system("adb -s %s pull /sdcard/Pictures/Screenshots/%s %s" % (self.dname, file_name, save_path))
        return save_path + '/' + file_name
