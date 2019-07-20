# -*- coding: utf-8 -*-
import base64
import os
import time

from adb_util import ADButil


# 点击某个图片
def screen_image_click(dName, image_name):
    adb = ADButil(dName)
    screen_image_path = adb.screenshot()
    pos = search_img(screen_image_path, image_name)
    adb.click(pos[0], pos[1])


# 分析search.jpg位置
def search_img(imgsrc, imgobj, confidencevalue=0.6, rgb=True):  # imgsrc=原始图像，imgobj=待查找的图片
    import aircv as ac
    print(imgsrc, imgobj)
    imsrc = ac.imread(imgsrc)
    imobj = ac.imread(imgobj)

    match_result = ac.find_template(imsrc, imobj,
                                    confidencevalue,
                                    rgb)  # {'confidence': 0.5435812473297119, 'rectangle': ((394, 384), (394, 416), (450, 384), (450, 416)), 'result': (422.0, 400.0)}
    if match_result is not None:
        match_result['shape'] = (imsrc.shape[1], imsrc.shape[0])  # 0为高，1为宽
    else:

        match_result = {'result': (-1, -1)}
    print(match_result)
    return match_result['result'][0], match_result['result'][1]


# ==========

def adb_input_keyevent(keycode, dname):
    # https://www.jianshu.com/p/bfc978d52e76
    os.system('adb -s %s shell input keyevent "%s"' % (dname, keycode))


def adb_input_text(text, dname):
    print(text)
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
        dname, base64.b64encode(text.encode('utf-8')).decode("utf-8")))
    time.sleep(2)
    os.system('adb -s %s  shell am broadcast -a ADB_EDITOR_CODE --ei code 4' % (dname))
    # os.system('adb -s %s shell input text "%s"' % (dname, text))  # 无法输入中文


def adb_click(x, y, dname):
    print(x, y, dname)
    if x == -1 and y == -1:
        return False
    os.system("adb -s %s shell input tap %d %d" % (dname, x, y))
    time.sleep(2)


def screen_cap(dname, file_name='screen.jpg', save_path=os.path.abspath('.')):
    # cmd adb shell screencap -p /sdcard/screen.jpg && adb pull /sdcard/screen.jpg
    print('截图' + dname)
    os.system("adb -s %s shell screencap -p /sdcard/DCIM/%s" % (dname, file_name))
    # 推送 到当前目录下
    os.system("adb -s %s pull /sdcard/DCIM/%s %s" % (dname, file_name, save_path))
