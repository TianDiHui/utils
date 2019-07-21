# -*- coding: utf-8 -*-
import base64
import os
import time






# 分析search.jpg位置
def search_img(imgsrc, imgobj, confidencevalue=0.7, rgb=True):  # imgsrc=原始图像，imgobj=待查找的图片
    try:
        import aircv as ac
        print(imgsrc, imgobj)
        imsrc = ac.imread(imgsrc)
        imobj = ac.imread(imgobj)
    except Exception as e:
        print (e)
        match_result = {'result': (-1, -1)}
        return match_result['result'][0], match_result['result'][1]

    match_result = ac.find_template(imsrc, imobj,
                                    confidencevalue,
                                    rgb)  # {'confidence': 0.5435812473297119, 'rectangle': ((394, 384), (394, 416), (450, 384), (450, 416)), 'result': (422.0, 400.0)}
    if match_result is not None:
        match_result['shape'] = (imsrc.shape[1], imsrc.shape[0])  # 0为高，1为宽
    else:

        match_result = {'result': (-1, -1)}
    print(match_result)
    return match_result['result'][0], match_result['result'][1]

