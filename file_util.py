# -*- coding: utf-8 -*-
import base64
import codecs
import datetime
import fnmatch
import glob
import hashlib
import json
import logging
import os
import re
import shutil
import time
from os.path import getsize, join
from shutil import copytree
from time import sleep

import xmltodict
from pip._vendor.distlib._backport.shutil import copystat

logger = logging.getLogger('django')
from .linux_util import is_linux_system
from .shell_util import exec_shell
from .string_util import timestamp_to_dbtime, covert_bytes
from .zip_util import zip_files


class Base64Img(object):

    def image_to_base64(self,img_path):

        with open(img_path, "rb") as f:
            # b64encode是编码，b64decode是解码
            base64_data = base64.b64encode(f.read())
            return base64_data

    def base64_to_image(self,base64_string, save_img_path):
        """
        base64字符转图片

        :param param1: this is a first param
        :param param2: this is a second param
        :returns: this is a description of what is returned
        :raises keyError: raises an exception
        @author： jhuang
        @time：22/03/2018
        """
        img_data = base64.b64decode(base64_string)
        with open(save_img_path, 'wb') as f:
            f.write(img_data)
        return save_img_path


def file_merge(src_file_list, dest_file):
    """
        合并文件

        :param param1: this is a first param
        :param param2: this is a second param
        :returns: this is a description of what is returned
        :raises keyError: raises an exception
        @author： jhuang
        @time：1/29/2018
    """
    logger.debug('合并文本内容至：%s' % dest_file)

    dest_file_handle = open(dest_file, 'w')
    for file_path in src_file_list:

        for line in open(file_path):
            # logger.debug(file_path)
            dest_file_handle.writelines(line)

        dest_file_handle.write('\n\r')
    dest_file_handle.close()
    return dest_file


def file_to_list(file_path):
    """
        读取文件到lists

        :param param1: this is a first param
        :param param2: this is a second param
        :returns: this is a description of what is returned
        :raises keyError: raises an exception
        @author： jhuang
        @time：1/22/2018
    """

    lists = []
    fd = file(file_path, "r")
    for line in fd.readlines():
        lists.append(str(line).replace("\n", ""))
    return lists


class JsonWR(object):
    """
        json文件读写

        :param param1: this is a first param
        :param param2: this is a second param
        :returns: this is a description of what is returned
        :raises keyError: raises an exception
        @author： jhuang
        @time：1/1/2018
    """

    def __init__(self, json_file):
        self.json_file = json_file

    def store(self, json_data):
        with open(self.json_file, 'w') as json_file:
            json_file.write(json.dumps(json_data))
            return json_data

    def load(self):
        with open(self.json_file) as json_file:
            # print json_file
            json_data = json.load(json_file)
            # print json_data
            return json_data


def get_file_md5(file_path):
    """
    |##desc: 获取文件MD5
    |##:param: None
    |##:return: None
    |##@author： jhuang
    |##@time：12/5/2017
    """
    if not os.path.exists(file_path):
        logger.error('文件不存在：%s' % (file_path))
        return ''
    with open(file_path, 'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        hash = md5obj.hexdigest()
        hash = str(hash).lower()
        return hash


def file_is_changeing(path):
    """
    |##desc: 判断文件是否正在更新
    |##:param: None
    |##:return: None
    |##@author： jhuang
    |##@time：11/1/2017
    """
    mtime1 = os.path.getmtime(path)
    print mtime1
    sleep(10)
    mtime2 = os.path.getmtime(path)
    print mtime2

    if mtime1 != mtime2:
        return True
    else:
        return False


def search_files(path, fnexp, limit=500, Case=True):
    """
    |##desc: 搜索文件
    |##:param: None
    |##:return: None
    |##@author： jhuang
    |##@time：2017/10/23
    """
    fileList = []

    print(path)
    print(fnexp)

    pattern = fnmatch.translate(fnexp)
    for path, dir, filelist in os.walk(path):
        for name in filelist:
            if Case == False:
                # 不区分大小写
                pattern = pattern.lower()
                name = name.lower()
            m = re.search(pattern, name)
            if m:
                file_path = os.path.join(path, name)
                print file_path
                fileList.append(file_path)
                if len(fileList) >= 500:
                    break

    print('搜索完成！查询到文件数：%s' % (len(fileList)))
    return fileList


def searchDirs(path, fnexp, limit=500, Case=True):
    """
    |##desc: 搜索文件夹
    |##:param: None
    |##:return: None
    |##@author： jhuang
    |##@time：2017/10/23
    """
    fileList = []

    print(path)
    print(fnexp)
    if Case == False:
        fnexp = fnexp.lower()
    pattern = fnmatch.translate(fnexp)
    for path, dir, filelist in os.walk(path):
        for name in dir:
            if Case == False:
                # 不区分大小写
                print pattern, name.lower()
                m = re.search(pattern, name.lower())
            else:
                m = re.search(pattern, name)
            if m:
                file_path = os.path.join(path, name)
                print file_path
                fileList.append(file_path)
                if len(fileList) >= 500:
                    break

    print('搜索完成！查询到文件数：%s' % (len(fileList)))
    return fileList


def search_files(path, fnexp, limit=500, Case=True):
    """
    |##desc: 搜索文件
    |##:param: None
    |##:return: None
    |##@author： jhuang
    |##@time：2017/10/23
    """
    fileList = []

    print(path)
    print(fnexp)
    if Case == False:
        fnexp = fnexp.lower()
    pattern = fnmatch.translate(fnexp)
    for path, dir, filelist in os.walk(path):
        for name in filelist:
            if Case == False:
                # 不区分大小写
                print pattern, name.lower()
                m = re.search(pattern, name.lower())
            else:
                m = re.search(pattern, name)
            if m:
                file_path = os.path.join(path, name)
                print file_path
                fileList.append(file_path)
                if len(fileList) >= 500:
                    break

    print('搜索完成！查询到文件数：%s' % (len(fileList)))
    return fileList


def get_dir_filelist_detail(dirPath, displayHidden=False):
    """
    |##desc: 将目录和文件列表转换为List
    |##:param: None
    |##:return: None
    |##@author： jhuang
    |##@time：2017/10/20
    """
    logger.debug(dirPath)
    dirList2 = []
    dirDic = {}
    dirDic['file_path'] = os.path.dirname(dirPath)
    dirDic['filename'] = '上一级目录..'
    dirDic['filetype'] = '目录'
    dirList2.append(dirDic)
    dirList = os.listdir(dirPath)
    for r in dirList:
        if displayHidden == False:
            if str(r)[0] == '.':
                continue

        dirDic = {}
        dirDic['filename'] = r
        dirDic['file_path'] = os.path.join(dirPath, r)
        dirDic['fileRelpath'] = os.path.join(dirPath, r)
        dirDic['mtime'] = timestamp_to_dbtime(os.path.getmtime(dirDic['file_path']))
        dirDic['ctime'] = timestamp_to_dbtime(os.path.getctime(dirDic['file_path']))
        dirDic['filesize'] = covert_bytes(os.path.getsize(dirDic['file_path']))
        if os.path.isdir(dirDic['file_path']):
            dirDic['filetype'] = '目录'
        else:
            dirDic['filetype'] = '文件'
        dirList2.append(dirDic)
    return dirList2


def get_dir_size(dir):
    """
    |##desc: # 获取文件夹大小
    |##:param: None
    |##:return: None
    |##@author： jhuang
    |##@time：9/1/2017
    """
    size = 0L
    for root, dirs, files in os.walk(dir):
        size += sum([getsize(join(root, name)) for name in files])
    return size


def get_file_size(path):
    """
    |##desc: # 获取文件大小
    |##:param: None
    |##:return: None
    |##@author： jhuang
    |##@time：9/1/2017
    """

    logger.debug(path)
    try:
        size = os.path.getsize(path)
        return size
    except Exception as err:

        logger.debug(err)
        return -1


def web_upload_file(request, upload_dir, upload_file_field='uploadfile'):
    """
    |##@Function purpose：通用上传接口
    |##@Parameter description：None
    |##@Return value：None
    |##@Function logic：None
    |##@author： jhuang
    |##@time：2017/6/16
    """
    if request.method == "POST":  # 请求方法为POST时，进行处理
        uploadFiles = request.FILES.get(upload_file_field, None)  # 获取上传的文件，如果没有文件，则默认为None
        if not uploadFiles:
            raise Exception("请上传文件!")
        uploadfilename = str(uploadFiles.name)
        print str(uploadfilename)[-4:].lower()

        # if str(uploadfilename)[-4:].lower() != '.zip' and str(uploadfilename)[-4:].lower() != '.war':
        #     return http_re_json("上传文件不合法，请上传.zip或.war文件！")

        today = datetime.datetime.today()
        uploadDir = upload_dir

        try:
            os.makedirs(uploadDir)
        except:
            pass
        fileSavePath = os.path.join(uploadDir, uploadFiles.name)
        logger.debug('打开特定的文件进行二进制的写操作 , 分块写入文件:%s  ' % (fileSavePath))
        destination = open(fileSavePath, 'wb+')
        for chunk in uploadFiles.chunks():
            destination.write(chunk)
        destination.close()
        logger.debug('文件上传成功：%s' % (fileSavePath))

        return fileSavePath


def sed_file(file_name, strOld, strNew):
    """
    | ##@函数目的: 替换文件指定内容（字符串）
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    with open(file_name, 'r') as r:
        lines = r.readlines()
    with open(file_name, 'w') as w:
        for l in lines:
            w.write(l.replace(strOld, strNew))


def remove_files(root_dir, ext, show=False):
    """
    删除rootdir目录下的符合的文件
    remove_files('.', '*.exe', show = True)
    """
    for i in files(root_dir, ext):
        if show:
            print i
        os.remove(i)


def files(curr_dir='.', ext='*.exe'):
    """当前目录下的文件"""
    for i in glob.glob(os.path.join(curr_dir, ext)):
        yield i


def dos2unix(filename):
    """
        |##desc: dos2unix
        |##:param: 文件路径
        |##:return: None
        |##@author： jhuang 参考：https://github.com/anir/dos2unix-python/blob/master/dos2unix.py
        |##@time：8/25/2017
    """
    text = open(filename, 'rb').read().replace('\r\n', '\n')
    open(filename, 'wb').write(text)


def unix2dos(filename):
    """
        |##desc: unix2dos
        |##:param: 文件路径
        |##:return: None
        |##@author： jhuang  参考：https://github.com/anir/dos2unix-python/blob/master/dos2unix.py
        |##@time：8/25/2017
    """
    text = open(filename, 'rb').read().replace('\n', '\r\n')
    open(filename, 'wb').write(text)


def dos2unix2(fname):
    """
    | ##@函数目的: windows格式文件转unix
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    src_file = fname
    dst_file = fname + '.dos'
    logger.debug('%s->%s' % (src_file, dst_file))
    src_fobj = open(src_file)
    dst_fobj = open(dst_file, 'w')
    for line in src_fobj:
        dst_fobj.write(line.rstrip('\r\n') + '\n')
    src_fobj.close()
    dst_fobj.close()
    return dst_file


def tail(file_path):
    """
    | ##@函数目的: 监控本地日志,输出到控制台
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    if is_linux_system is True:
        os.system('tail -f ' + file_path)
    else:
        return u'非linux系统无法查看日志...'


def copytree2(src, dst, symlinks=False):
    """
    | ##@函数目的: 复制文件夹(解决copytree不能覆盖的问题以及目标文件夹存在出异常问题)
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    logger.debug('copytree2 > %s->%s' % (src, dst))
    names = os.listdir(src)
    if not os.path.isdir(dst):
        os.makedirs(dst)

    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                pass
                # linkto = os.readlink(srcname)
                # os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks)
            else:
                if os.path.isdir(dstname):
                    os.rmdir(dstname)
                elif os.path.isfile(dstname):
                    os.remove(dstname)
                shutil.copy2(srcname, dstname)
                # XXX What about devices, sockets etc.?
        except (IOError, os.error) as why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except OSError as err:
            errors.extend(err.args[0])
    try:
        copystat(src, dst)
    except WindowsError:
        # can't copy file access times on Windows
        pass
    except OSError as why:
        errors.extend((src, dst, str(why)))
    if errors:
        raise str(errors)


def processDirectory(args, dirname, filenames):
    logger.debug('Directory : %s ' % dirname)
    for filename in filenames:
        logger.debug(' File:%s' % filename)


def delete_expire_file(path, expiredTime_min):
    """
    | ##@函数目的: 遍历删除过期文件
    | ##@参数说明：expiredTime_min 单位分钟
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    for obj in os.listdir(path):
        objpath = os.path.join(path, obj)
        if os.path.isfile(objpath):
            _delete_expire_file(objpath, expiredTime_min)
        elif os.path.isdir(objpath):
            delete_expire_file(objpath, expiredTime_min)


def _delete_expire_file(file_path, expiredTime_min):
    expiredsec = expiredTime_min * 60
    stat_result = os.stat(file_path)
    ctime = stat_result.st_mtime
    ntime = time.time()
    if (ntime - ctime) > expiredsec:
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                logger.debug('del file: %s' % (file_path))
        except Exception as e:
            logger.debug(e)
    else:
        return False


def mysql_backup(db_host, db_user, db_passwd, db_name, backupdir):
    """
    | ##@函数目的: 备份mysql数据库
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    db_charset = "utf8"
    logger.debug('清理三天前的备份数据...')
    delete_expire_file(backupdir, 60 * 24 * 3)
    zip_src = "%s/%s_%s_%s.sql" % (backupdir, db_host, db_name, time.strftime("%Y%m%d%H%M"))
    zip_dest = zip_src + ".zip"
    logger.debug("dump mysql database ...")
    cmd = "mysqldump -h%s -u%s -p%s %s --default_character-set=%s > %s" % (
        db_host, db_user, db_passwd, db_name, db_charset, zip_src)
    exec_shell(cmd)
    zip_files(zip_src, zip_dest, True)
    logger.debug("done, mysql backup complete!")


def file_writes(file_path, text):
    """
    |##@函数目的：写入文件，一次性
    |##@参数说明：
    |##@返回值：
    |##@函数逻辑：
    |##@开发人：runksun,jhuang
    |##@时间：2016年11月16日
    """
    if not os.path.isfile(file_path):
        logger.debug(u'文件不存在:%s' % (file_path))
        # file_path= tempfile.mktemp()
    logger.debug(u'file_writes->%s' % (file_path))
    f = codecs.open(file_path, 'w', 'utf-8')
    f.write(text)
    f.close()
    return file_path


def get_url_filename(url):
    """
    |##@函数目的：获取URL地址中的文件名
    |##@参数说明：
    |##@返回值：
    |##@函数逻辑：
    |##@开发人：jhuang
    |##@时间：
    """
    filename = str(os.path.basename(url))
    return filename


def file_path_parse(file_path, iType=0):
    """
    |##@函数目的：解析和返回文件路径中文件名或扩展名
    |##@参数说明：file_path 文件全路径
    |##@返回值：iType =1 文件名 iType=0 扩展名 iType=2 文件名+扩展名
    |##@函数逻辑：无
    |##@开发人：jhuang
    |##@时间：
    """
    if iType == 0:
        ret = os.path.basename(file_path).split('.')[-1]  # 扩展名  txt
    elif iType == 1:  # 文件名
        ret = os.path.basename(file_path).split('.')[0]
    elif iType == 2:  # 文件名+扩展名
        ret = os.path.basename(file_path)
    elif iType == 3:  # 获取目录
        ret = os.path.split(file_path)[0]
    else:
        ret = os.path.basename(file_path)
    return ret





def file_reads(file_path):
    """
    | ##@函数目的: 文件读取
    | ##@参数说明：
    | ##@返回值：无
    | ##@开发人：jhuang
    | ##@函数逻辑：
    """
    logger.debug(file_path)
    if not os.path.exists(file_path):
        logger.exception('文件不存在:%s' % (file_path))
        return ''
    file_object = open(file_path)
    try:
        all_the_text = file_object.read()
    finally:
        file_object.close()
    return all_the_text


def get_bigfile_md5(self, file_path):
    """
    | ##@函数目的: 获取文件MD5值
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    if self.isFile(file_path):
        md5obj = hashlib.md5()
        maxbuf = 8192
        f = open(file_path, 'rb')
        while True:
            buf = f.read(maxbuf)
            if not buf:
                break
            md5obj.update(buf)
        f.close()
        hash = md5obj.hexdigest()
        return str(hash).upper()
    return None
