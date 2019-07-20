# -*- coding: utf-8 -*-

# http://www.oschina.net/project/tag/172/wysiwyg/
import datetime
import json
import os
import re
import time

from django.http.response import HttpResponse

import string_util
from SRMCenter.apps.global_var import  GlobalVar
logger = logging.getLogger('django')


def kindeditor_fileManager_to_json(request):
    """
    |##@函数目的：kinde浏览附件
    |##@参数说明：
    |##@返回值：
    |##@函数逻辑：
    |##@开发人：jhuang
    |##@时间：
    参考:http://blog.csdn.net/xiaoqi030611a/article/details/8308808
    """
    MEDIA_URL = request.get_host()
    root_path = os.path.join(GlobalVar.project_dir, 'SRMCenter', 'static', 'attached')
    root_url = MEDIA_URL + "/static/attached/"
    file_types = ["gif", "jpg", "jpeg", "png", "bmp"]
    dir_types = ['image', 'flash', 'media', 'file']

    dir_name = request.GET["dir"]

    if dir_name:
        if dir_name not in dir_types:
            logger.debug("Invalid Directory name.")
            return
        root_path = os.path.join(root_path, dir_name) + "/"
        logger.debug(root_path)
        root_url = root_url + dir_name + "/"
        if not os.path.isdir(root_path) or not os.path.exists(root_path):
            os.makedirs(root_path)

    path = request.GET["path"]
    if not path:
        path = ""
    current_path = root_path + path
    current_url = root_url + path
    current_dir_path = path
    moveup_dir_path = ""

    if path:
        m = re.search(r'(.*?)[^\/]+\/$', current_dir_path)
        moveup_dir_path = m.group(1)

    order = request.GET["order"]
    if order:
        order = string_util.lower(order)
    else:
        order = "name"

    if ".." in current_path:
        logger.debug("Access is not allowed.")
        return

    if re.search(r'(\/$)', current_path).group(0) != '/':
        logger.debug("Parameter is not valid.")
        return

    if not os.path.isdir(current_path) or not os.path.exists(current_path):
        logger.debug("'Directory does not exist.")
        return

    file_list = []
    if os.listdir(current_path):
        for file_name in os.listdir(current_path):
            dicts = {}
            file_path = current_path + file_name
            if os.path.isdir(file_path):
                dicts["is_dir"] = True
                dicts["has_file"] = len(os.listdir(file_path)) > 0
                dicts["filesize"] = 0
                dicts["is_photo"] = False
                dicts["filetype"] = ""
            else:
                dicts["is_dir"] = False
                dicts["has_file"] = False
                dicts["filesize"] = os.path.getsize(file_path)

                extensions = string_util.split(file_name, ".")
                length = len(extensions) - 1
                if string_util.lower(extensions[length]) in file_types:
                    dicts["is_photo"] = True
                else:
                    dicts["is_photo"] = False
            dicts["filetype"] = ''
            dicts["filename"] = file_name
            dicts["datetime"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            file_list.append(dicts)

    results = {}
    results["moveup_dir_path"] = moveup_dir_path
    results["current_dir_path"] = current_dir_path
    results["current_url"] = current_url
    results["total_count"] = len(file_list)
    results["file_list"] = file_list

    return HttpResponse(json.dumps(results))


def kindeditor_upload_file(request):
    """
    |##@函数目的：kinde上传文件
    |##@参数说明：
    |##@返回值：
    |##@函数逻辑：
    |##@开发人：jhuang
    |##@时间：
    参考:http://blog.csdn.net/xiaoqi030611a/article/details/8308808
    """
    ext_allowed = {}
    ext_allowed["image"] = ['gif', 'jpg', 'jpeg', 'png']
    ext_allowed["flash"] = ["swf", "flv"]
    ext_allowed["media"] = ["swf", "flv", "mp3", "wav", "wma", "wmv", "mid", "avi", "mpg", "asf", "rm", "rmvb"]
    # ext_allowed["file"] = ["doc", "docx", "xls", "xlsx", "ppt", "htm", "html", "txt", "zip", "rar", "gz" , "bz2"]
    ext_allowed["file"] = ["xml", "zip", 'xml', 'txt']

    max_size = 1000000
    today = datetime.datetime.today()
    dir_name = request.GET["dir"]
    save_dir = '/attached/' + dir_name + '/%d/%d/%d/' % (today.year, today.month, today.day)  # 按天存放
    save_path = os.path.join(GlobalVar.project_dir, 'SRMCenter', 'static') + save_dir  # 保存路径
    logger.debug('保存上传附件:%s' % (save_path))
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    MEDIA_URL = request.get_host()
    logger.debug('MEDIA_URL' + MEDIA_URL)
    save_url = "http://" + MEDIA_URL + '/static/' + save_dir
    logger.debug('save_url:' + save_url)

    if request.method == 'POST':
        file_content = request.FILES['imgFile']

        if not file_content.name:
            return HttpResponse(json.dumps(
                {'error': 1, 'message': '请选择要上传的文件'}
            ))

        ext = file_content.name.split('.').pop()

        if ext not in ext_allowed[dir_name]:
            return HttpResponse(json.dumps(
                {'error': 1, 'message': '请上传后缀为%s的文件' % ext_allowed[dir_name]}
            ))

        if file_content.size > max_size:
            return HttpResponse(json.dumps(
                {'error': 1, 'message': '上传的文件大小不能超过10MB'}
            ))

        if not os.path.isdir(save_path):
            os.makedirs(save_path)

        new_file = '%s.%s' % (int(time.time()), ext)

        destination = open(save_path + new_file, 'wb+')
        for chunk in file_content.chunks():
            destination.write(chunk)
        destination.close()

        return HttpResponse(json.dumps(
            {'error': 0, 'url': save_url + new_file}
        ))
