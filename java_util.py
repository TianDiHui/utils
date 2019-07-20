# -*- coding: utf-8 -*-

# https://www.ibm.com/developerworks/cn/opensource/os-cn-jpype/
import jpype

logger = logging.getLogger('django')


class JavaClass(object):
    """
    加载jar

    :param param1: this is a first param
    :param param2: this is a second param
    :returns: this is a description of what is returned
    :raises keyError: raises an exception
    @author： jhuang
    @time：27/04/2018
    """

    def __init__(self, jar_path_list):
        self.jar_path_list = jar_path_list
        self.jpype = jpype
        self.jdk_version = None

    def start_jvm(self):
        if self.jpype.isJVMStarted():
            return
        jar_path_list = []
        for r in self.jar_path_list:
            r = "-Djava.class.path=%s" % (r)
            jar_path_list.append(r)
        jar_path = " ".join(jar_path_list)
        logger.debug(jar_path)
        self.jpype.startJVM(jpype.getDefaultJVMPath(), jar_path,'-XX:ErrorFile=./hs_err_pid.log')
        self.jpype.attachThreadToJVM()
        self.jdk_version = (jpype.java.lang.System.getProperty("java.version"))
        logger.debug('jdk version:%s' % (self.jdk_version))

    def attch_thread_to_jvm(self):
        # 附属线程到JVM
        self.jpype.attachThreadToJVM()

    def __del__(self):
        self.shutdown_jvm()

    def shutdown_jvm(self):
        self.jpype.shutdownJVM()



