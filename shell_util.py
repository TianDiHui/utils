# -*- coding: utf-8 -*-
import os
import subprocess
import time

logger = logging.getLogger('django')
from EasyProcess_util import EasyProcess2


def subprocess_to_log(cmd, log_path='', cwd=None):
    """
    有了subprocess之后，生活变得更加美好了，但是，上面的代码一不小心就会让你掉入难以追查的坑中，subprocess调用的子进程可能hang住，而poll会永远无法等到子进程结束。Complete deadlock!

经过多次试错后发现，cmd命令输出（标准或者错误）小于65536字节时，程序运行完全正常，当输出大于等于65536后，程序立马hang住，看来问题就可能出在输出过多数据上。

    |##@函数目的：执行本地命令,并将控制台结果输出到日志
    |##@参数说明：shell=True  表示调用本地的shell，必选。
                            stdout=subprocess.PIPE
                            stderr=subprocess.PIPE
                             
                            分表把stdout和stderr重定向到PIPE这个对象里面。进行缓存。
                            也可以在调用多个subprocess的时候，进行通信。
                            cwd ： 进入的工作目录
    |##@返回值：
    |##@函数逻辑：无
    |##@开发人：jhuang
    |##@时间：
    """
    logger.debug('%s \ncwd:%s' % (cmd, cwd))
    f = None
    if os.path.exists(log_path):
        f = file(log_path, "a+")
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         cwd=cwd)

    lists = []
    while p.poll() == None:
        for o in iter(p.stdout.readline, ''):
            logger.debug(o)
            if f != None:
                f.writelines(o)
                lists.append(o)
        for e in iter(p.stderr.readline, ''):
            logger.debug(e)
            if f != None:
                f.writelines(e)
                lists.append(e)

    if f != None: f.close()
    logger.debug('%s ->rc:%s' % (cmd, p.returncode))
    ret = ''.join(lists)
    return str(ret), str(p.returncode)


def exec_shell(cmd, timeout=10 * 60, cwd=None, log=True,env=None):
    """
    |##@函数目的：执行本地命令
    |##@参数说明：无
    |##@返回值：
    |##@函数逻辑：无
    |##@开发人：jhuang
    |##@时间：
    """
    start = time.time()

    if log is True:
        logger.debug(cmd)

    (output, status, pid) = execute_command(cmd, cwd, timeout, log=log,env=env)
    output = unicode(str(output), errors='replace').encode('utf-8')
    output = str(output)
    status = str(status)
    if log:
        logger.debug('(RC=%s,PID:%s)(返回)->%s \n用时：%s\n\返回结果=%s' % (status, pid, cmd, time.time() - start, output))

    dic = {}
    dic['msg'] = output
    dic['rc'] = status
    dic['pid'] = str(pid)
    return dic


def execute_command(cmdstring, cwd=None, timeout=None, shell=True, log=True,env=None):
    """
     |##@函数目的：执行本地命令 https://github.com/ponty/EasyProcess
     |##@参数说明：无
     |##@返回值：
     |##@函数逻辑：无
     |##@开发人：jhuang
     |##@时间：
     """

    s = EasyProcess2(cmdstring,env=env).call(timeout=timeout)
    logger.debug(env)
    stderr = s.stderr
    stdout = s.stdout
    returnText = stdout + stderr
    returncode = s.return_code
    pid = '0'
    return str(returnText), str(returncode).strip(), pid
