# -*- coding: utf-8 -*-
import os
import shutil
import time
import zipfile

from pip._vendor.distlib.compat import ZipFile

logger = logging.getLogger('django')
from linux_util import is_linux_system
from shell_util import exec_shell


def zip_extract(zip_file, extract_file_list, extract_dir):
    """
        解压zip中的指定文件

        :param param1: this is a first param
        :param param2: ['WEB-INF/classes/META-INF/global.properties']
        :returns: this is a description of what is returned
        :raises keyError: raises an exception
        @author： jhuang
        @time：1/24/2018
    """

    time_start = time.time()
    logger.debug('zip:%s , extract_file_list:%s，extract_dir：%s' % (zip_file, extract_file_list, extract_dir))
    zipFile = zipfile.ZipFile(os.path.join(os.getcwd(), zip_file))

    extract_file_list_dest = []
    for file in extract_file_list:
        if file[0] == '/':
            file = file[1:]
        if os.path.exists(os.path.join(extract_dir, file)):
            logger.debug('删除文件:%s' % (os.path.join(extract_dir, file)))
            os.remove(os.path.join(extract_dir, file))

        zipFile.extract(file, extract_dir)
        extract_file_list_dest.append(os.path.join(extract_dir, file))
    logger.debug('解压文件用时：%s' % (time.time() - time_start))
    return extract_file_list_dest


def zip_file_add(zip_file, new_file_path_list, new_file_path_rel_list):
    """
        将文件添加更新到zip文件

        :param param1: this is a first param
        :param param2: ['WEB-INF/classes/META-INF/global.properties']
        :returns: this is a description of what is returned
        :raises keyError: raises an exception
        @author： jhuang
        @time：1/24/2018
    """
    time_start = time.time()
    logger.debug(new_file_path_list)

    n = 0
    for file in new_file_path_list:
        exec_shell('zip -d %s %s' % (zip_file, new_file_path_rel_list[n]))
        n = +1

    f = zipfile.ZipFile(zip_file, 'a', zipfile.ZIP_DEFLATED)
    n = 0
    for file in new_file_path_list:
        f.write(file, new_file_path_rel_list[n])
        n = +1
    f.close()
    logger.debug('更新压缩文件用时：%s' % (time.time() - time_start))


def get_zip_file_list(file_path):
    """
    | ##@函数目的: 读取压缩包的文件列表
    | ##@参数说明：
    | ##@返回值：LIST
    | ##@开发人：jhuang
    | ##@函数逻辑：
    """
    if not os.path.isfile(str(file_path)):
        logger.error('待预览压缩包文件不存在：%s' % (file_path))
        return False
    zfobj = zipfile.ZipFile(file_path)
    oinfp_list = ZipFile.namelist(zfobj)
    filelist = []
    for r in oinfp_list:
        filelist.append(r)
    return filelist


def zip_files(zip_src, zip_dest, fullpath=False, removeSrc=False):
    """
    | ##@函数目的: 压缩指定文件为zip文件
    | ##@参数说明：
    | ##@返回值：
    | ##@开发人：jhuang
    | ##@函数逻辑：
    """
    logger.debug('%s->%s' % (zip_src, zip_dest))
    f = zipfile.ZipFile(zip_dest, 'w', zipfile.ZIP_DEFLATED)
    if fullpath:
        f.write(zip_src, )
    else:
        f.write(zip_src, os.path.basename(zip_src))
    f.close()
    if removeSrc is True:
        logger.debug('清理源文件: %s' % (zip_src))
        if os.path.exists(zip_src):
            os.remove(zip_src)


def zip_dir(dir_path, file_path, listsNozipFiles=[], listsNozipDirs=[]):
    """
    | ##@函数目的: 压缩指定目录为zip文件
    | ##@参数说明：dirname为指定的目录，zipfilename为压缩后的zip文件路径  listsNozipFiles 排除压缩的文件列表
    | ##@返回值：无
    | ##@开发人：jhuang
    | ##@函数逻辑：
    """

    filelist = []
    if os.path.isfile(dir_path):
        filelist.append(dir_path)
    else:
        for root, dirs, files in os.walk(dir_path):
            for name in files:
                filelist.append(os.path.join(root, name))
    zf = zipfile.ZipFile(file_path, "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        arcname = tar[len(dir_path):]
        zf.write(tar, arcname)
    zf.close()


def unzip(zip_file_path, unzip_to_dir):
    """
    | ##@函数目的: 解压zip文件到指定目录
    | ##@参数说明：zipfilename为zip文件路径，unziptodir为解压文件后的文件目录
    | ##@返回值：无
    | ##@开发人：jhuang
    | ##@函数逻辑：
    """
    if not os.path.isfile(zip_file_path):
        logger.error('待解压文件不存在：%s' % (zip_file_path))
        return False
    logger.debug( zip_file_path + '->' + unzip_to_dir)
    ret = exec_shell('unzip')
    if 'Usage' in str(ret['msg']):
        logger.debug('存在unzip命令,使用unzip命令解压...')
        if is_linux_system():
            exec_shell('unzip -o %s -d %s > %s_unzip.log 2>&1' % (zip_file_path, unzip_to_dir, zip_file_path))
        else:
            exec_shell('unzip -o %s -d %s  > %s_unzip.log' % (zip_file_path, unzip_to_dir, zip_file_path))
    else:
        if not os.path.exists(unzip_to_dir):
            os.mkdir(unzip_to_dir)
        zfobj = zipfile.ZipFile(zip_file_path)
        for name in zfobj.namelist():
            name = name.replace('\\', '/')
            if name.endswith('/'):
                p = os.path.join(unzip_to_dir, name[:-1])
                if os.path.exists(p):
                    # 如果文件夹存在，就删除之：避免有新更新无法复制
                    shutil.rmtree(p)
                os.mkdir(p)
            else:
                ext_filename = os.path.join(unzip_to_dir, name)
                ext_dir = os.path.dirname(ext_filename)
                if not os.path.exists(ext_dir):
                    os.mkdir(ext_dir, 0777)
                outfile = open(ext_filename, 'wb')
                outfile.write(zfobj.read(name))
                outfile.close()
