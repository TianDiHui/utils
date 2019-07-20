# -*- coding: utf-8 -*-

class NexusClass():
    """
    初始化nexus实例
    @author： lanxiong
    @time：2018/7/3
    """

    def __init__(self,
                 nexus_url="",
                 nexus_user="",
                 nexus_pwd="",
                 nexus_groupid="",
                 nexus_repository="",
                 nexus_soft_artifact="",
                 nexus_soft_version=""
                 ):
        self.nexus_url = nexus_url
        self.nexus_user = nexus_user
        self.nexus_pwd = nexus_pwd
        self.nexus_groupid = nexus_groupid
        self.nexus_repository = nexus_repository
        self.nexus_soft_artifact = nexus_soft_artifact
        self.nexus_soft_version = nexus_soft_version

    def get_nexus_soft_download_url(self):
        """
        获取软件下载链接
        @author： lanxiong
        @time：2018/7/3
        """
        nexus_soft_download_url = """{nexus_url}/nexus/service/local/artifact/maven/redirect?r={nexus_repository}&g={nexus_groupid}&a={nexus_soft_artifact}&e=zip&v={nexus_soft_version}""".format(nexus_url = self.nexus_url,
                   nexus_repository = self.nexus_repository,
                   nexus_groupid = self.nexus_groupid,
                   nexus_soft_artifact = self.nexus_soft_artifact,
                   nexus_soft_version = self.nexus_soft_version
                   )
        return nexus_soft_download_url
