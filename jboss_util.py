# -*- coding: utf-8 -*-
import os
import time

from SRMCenter.apps.global_var import GlobalVar
logger = logging.getLogger('django')
from shell_util import exec_shell


# 参考文档：http://planet.jboss.org/post/deploy_to_wildfly_using_jboss_cli_tech_tip_11


def jboss_enable(jboss_cli_home, server_ip, jboss_admin_port, jboss_admin, jboss_admin_pwd, artifact_id,
                 timeout='60000'):
    """
    | ##@函数目的: 启动WAR包
    | ##@参数说明：timeout 毫秒 对于网络差或目标服务器差的适当加大  jboss_admin_port 默认(无偏移量)9999
    | ##@返回值：
    | ##@函数逻辑：./jboss-cli.sh --connect command=:shutdown
    | ##@开发人：jhuang
    | ##@时间：
    """
    time_start = time.time()

    jboss_cli = 'jboss-cli.sh'
    if jboss_cli_home[-1] != '/': jboss_cli_home = jboss_cli_home + '/'
    ret = exec_shell(
        '/bin/sh %sbin/%s --connect --controller=%s:%s --user=%s --password=%s --timeout=%s --command="deploy --name=%s"' % (
            jboss_cli_home, jboss_cli, server_ip, jboss_admin_port, jboss_admin, jboss_admin_pwd, timeout,
            artifact_id))

    logger.debug('启用Artifact用时：%s' % (time.time() - time_start))

    return ret


def jboss_disable(jboss_cli_home, server_ip, jboss_admin_port, jboss_admin, jboss_admin_pwd, artifact_id,
                  timeout='60000'):
    """
    | ##@函数目的: 禁用WAR包
    | ##@参数说明：timeout 毫秒 对于网络差或目标服务器差的适当加大
    | ##@返回值：
    | ##@函数逻辑：./jboss-cli.sh --connect command=:shutdown
    | ##@开发人：jhuang
    | ##@时间：
    """
    time_start = time.time()
    jboss_cli = 'jboss-cli.sh'
    if jboss_cli_home[-1] != '/': jboss_cli_home = jboss_cli_home + '/'
    ret = exec_shell(
        '/bin/sh %sbin/%s --connect --controller=%s:%s --user=%s --password=%s --timeout=%s --command="undeploy %s --keep-content"' % (
            jboss_cli_home, jboss_cli, server_ip, jboss_admin_port, jboss_admin, jboss_admin_pwd, timeout,
            artifact_id))

    logger.debug('禁用Artifact用时：%s' % (time.time() - time_start))
    return ret


def jboss_shutdown(jboss_cli_home, server_ip, jboss_admin_port, jboss_admin, jboss_admin_pwd, timeout='60000'):
    """
    | ##@函数目的: Jboss卸载WAR包
    | ##@参数说明：timeout 毫秒 对于网络差或目标服务器差的适当加大
    | ##@返回值：
    | ##@函数逻辑：./jboss-cli.sh --connect command=:shutdown
    | ##@开发人：jhuang
    | ##@时间：
    """

    jboss_cli = 'jboss-cli.sh'
    if jboss_cli_home[-1] != '/': jboss_cli_home = jboss_cli_home + '/'
    ret = exec_shell(
        '/bin/sh %sbin/%s --connect --controller=%s:%s --user=%s --password=%s --timeout=%s --command=:shutdown' % (
            jboss_cli_home, jboss_cli, server_ip, jboss_admin_port, jboss_admin, jboss_admin_pwd, timeout))

    return ret


def kill_repeat_jboss(server_ip, jboss_admin_port, warName):
    logger.debug('关闭相同任务进程...')
    jboss_cli_kill_path = os.path.join(GlobalVar.app_dir, 'plugins', 'shell', 'jboss_cli_kill.sh')
    exec_shell('chmod +x %s' % (jboss_cli_kill_path))
    exec_shell(jboss_cli_kill_path + ' %s:%s %s' % (server_ip, jboss_admin_port, warName))


# jboss-cli.bat --connect --controller=192.168.222.61:9999 --user=admin --password=thzk211! --command="deploy -l"  --timeout=60000
def jboss_undeploy(jboss_cli_home, server_ip, jboss_admin_port, jboss_admin, jboss_admin_pwd, artifact_id,
                   timeout='60000'):
    """
    | ##@函数目的: Jboss卸载WAR包
    | ##@参数说明：timeout 毫秒 对于网络差或目标服务器差的适当加大
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    time_start = time.time()

    jboss_cli = 'jboss-cli.sh'
    if jboss_cli_home[-1] != '/': jboss_cli_home = jboss_cli_home + '/'
    ret = exec_shell(
        'sh %sbin/%s --connect --controller=%s:%s --user=%s --password=%s --command="undeploy   %s" --timeout=%s' % (
            jboss_cli_home, jboss_cli, server_ip, jboss_admin_port, jboss_admin, jboss_admin_pwd, artifact_id,
            timeout))

    logger.debug('卸载用时：%s' % (time.time() - time_start))
    return ret


def jboss_deploy(jboss_cli_home, server_ip, jboss_admin_port, jboss_admin, jboss_admin_pwd, warpath, timeout='60000'):
    """
    | ##@函数目的: Jboss部署WAR包
    | ##@参数说明：timeout 毫秒 对于网络差或目标服务器差的适当加大
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    time_start = time.time()

    jboss_cli = 'jboss-cli.sh'
    if jboss_cli_home[-1] != '/': jboss_cli_home = jboss_cli_home + '/'
    ret = exec_shell(
        'sh %sbin/%s --connect --controller=%s:%s --user=%s --password=%s --command="deploy  --force %s" --timeout=%s' % (
            jboss_cli_home, jboss_cli, server_ip, jboss_admin_port, jboss_admin, jboss_admin_pwd, warpath, timeout))

    logger.debug('部署用时：%s' % (time.time() - time_start))
    return ret


def jboss_status(jboss_cli_home, server_ip, jboss_admin_port, jboss_admin, jboss_admin_pwd, timeout='60000'):
    """
    | ##@函数目的: Jboss状态
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    time_start = time.time()

    jboss_cli = 'jboss-cli.sh'
    if jboss_cli_home[-1] != '/': jboss_cli_home = jboss_cli_home + '/'
    ret = exec_shell(
        'sh %sbin/%s --connect --controller=%s:%s --user=%s --password=%s --command="deployment-info" --timeout=%s' % (
            jboss_cli_home, jboss_cli, server_ip, jboss_admin_port, jboss_admin, jboss_admin_pwd, timeout))

    logger.debug('获取Jboss状态用时：%s' % (time.time() - time_start))
    return ret


def jboss_deploy_status(jboss_cli_home, server_ip, jboss_admin_port, jboss_admin, jboss_admin_pwd, artifact_id,
                        timeout='60000'):
    """
    | ##@函数目的: JbossWAR包状态
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    time_start = time.time()

    jboss_cli = 'jboss-cli.sh'
    if jboss_cli_home[-1] != '/': jboss_cli_home = jboss_cli_home + '/'
    ret = exec_shell(
        'sh %sbin/%s --connect --controller=%s:%s --user=%s --password=%s --command="deployment-info --name=%s" --timeout=%s' % (
            jboss_cli_home, jboss_cli, server_ip, jboss_admin_port, jboss_admin, jboss_admin_pwd, artifact_id, timeout))

    logger.debug('获取应用部署状态用时：%s' % (time.time() - time_start))

    return ret
