# -*- coding: utf-8 -*-
# 官方文档: http://pythonhosted.org/jira/#python
# 示例文档:http://jira.readthedocs.io/en/latest/examples.html#attachments
'''
jiar操作类
author:  jhuang ,  rksun
'''

import re

from jira import JIRA

from utils.common_util import get_except
from http_util import HttpClass
logger = logging.getLogger('django')

JiraList = []


class JiraClass():
    def __init__(self):
        self.username = None
        self.password = None
        self.jira = None

        self.jira_server_url = None

    def web_login(self, url, username, password):
        """
        | ##@函数目的: 登录
        | ##@参数说明：
        | ##@返回值：登录句柄
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        self.jira_server_url = url
        if self.jira_server_url[-1] == '/':
            self.jira_server_url = self.jira_server_ur[:-1]
        data = {'login': '%E7%99%BB%E5%BD%95',
                'os_username': username,
                'os_password': password,
                'os_destination': '',
                'atl_token': type
                }

        self.ohttp = HttpClass()
        logger.debug('登录Jira..user:%s,pwd:%s' % (username, '*'))
        ret, html = self.ohttp.post(self.jira_server_url + '/login.jsp', data)
        if not '登录' in html:
            logger.debug('登录JIRA成功!')
        else:
            logger.exception('登录JIRA失败!')

        return self.ohttp

    def connect(self, jira_server_url, username, password):
        '''
        [方法说明]
            初始化连接(认证,获取对象)
        [参数说明]
            server:服务器URL
            username:登陆用户名
            password:登陆密码    
        [实例]
            jira_connect('http://www.tjhcc.com.cn:91','jhuang', '****.')
        '''

        self.jira_server_url = jira_server_url
        if self.jira_server_url[-1] == '/':
            self.jira_server_url = self.jira_server_url[:-1]
        self.username = username
        self.password = password

        jira_options = {'server': jira_server_url, 'verify': False}

        logger.debug('连接Jira:%s (%s)' % (jira_server_url, username))
        jira = JIRA(options=jira_options, basic_auth=(username, password))
        self.jira = jira
        return self.jira

    def update_fields(self, issue_key, fields_dict):
        """
        更新jira自定义字段:https://jira.readthedocs.io/en/master/examples.html#fields

        :param fields_dict: {'customfield_11403': 1}
        :param issue_key: pms-299
        :returns: this is a description of what is returned
        :raises keyError: raises an exception
        @author： jhuang
        @time：10/10/2018
        """
        issue = self.jira.issue(issue_key)

        for idct_key in fields_dict:
            fields = idct_key

        all_fields_dict = issue.raw['fields']

        text = 0
        for all_fields_dict_one in all_fields_dict:
            if all_fields_dict_one.find(fields):
                text = 1
        if text == 0:
            return 0
        try:
            issue.update(fields=fields_dict)
        except Exception as e:
            return get_except(e)


    def comment(self, issueKey, comment):
        '''
        添加评论
        [参数说明]
            issuenum:issue号 
        '''
        # 解决命令行参数:中文问题.decode("GBK")
        logger.debug('提交jira备注:%s至:%s' % (comment, issueKey))
        # comment = self.jira.add_comment(issueKey, comment.decode("GBK"))
        comment = self.jira.add_comment(issueKey, comment)

    def resolve_issue(self, issueKey, resolution='6'):
        '''
        解决ISSUE
        [参数说明]
            issuenum:issue号 
        '''
        try:
            logger.debug('解决jira::%s' % (issueKey))
            self.jira.transition_issue(issueKey, '%s' % ('5'), None, resolution={'id': '%s' % resolution})
        except Exception as e:
            get_except(e)

    def queryIssueLink(self, issueKey):
        """查询关联的ISSUE"""
        oIssue = self.jira.issue('ZJYYXM-201')
        '''
In [2]: issue.
issue.delete  issue.fields  issue.id      issue.raw     issue.update
issue.expand  issue.find    issue.key     issue.self

In [2]: issue.fields.
issue.fields.aggregateprogress              issue.fields.customfield_11531
issue.fields.aggregatetimeestimate          issue.fields.customfield_11631
issue.fields.aggregatetimeoriginalestimate  issue.fields.customfield_11930
issue.fields.aggregatetimespent             issue.fields.customfield_12130
issue.fields.assignee                       issue.fields.customfield_12131
issue.fields.attachment                     issue.fields.description
issue.fields.comment                        issue.fields.environment
issue.fields.components                     issue.fields.fixVersions
issue.fields.created                        issue.fields.issuelinks
issue.fields.customfield_10150              issue.fields.issuetype
issue.fields.customfield_10160              issue.fields.labels
issue.fields.customfield_10161              issue.fields.mro
issue.fields.customfield_10180              issue.fields.progress
issue.fields.customfield_10230              issue.fields.project
issue.fields.customfield_10575              issue.fields.reporter
issue.fields.customfield_10610              issue.fields.resolution
issue.fields.customfield_10650              issue.fields.resolutiondate
issue.fields.customfield_10651              issue.fields.status
issue.fields.customfield_10680              issue.fields.subtasks
issue.fields.customfield_10723              issue.fields.summary
issue.fields.customfield_11130              issue.fields.timeestimate
issue.fields.customfield_11230              issue.fields.timeoriginalestimate
issue.fields.customfield_11431              issue.fields.timespent
issue.fields.customfield_11433              issue.fields.updated
issue.fields.customfield_11434              issue.fields.versions
issue.fields.customfield_11435              issue.fields.votes
issue.fields.customfield_11436              issue.fields.watches
issue.fields.customfield_11437              issue.fields.workratio'''
        #             logger.info ('关联的ISSUE:%s' %(oIssue.fields.attachment))
        for IssueLink in oIssue.fields.RemoteLinks:
            print IssueLink

    def _search_issue(self, searchText, childTask=False):
        """
        |##desc: 子函数  支持包含多个KEY的LIST 返回： list
        |##:param: None
        |##:return: None
        |##@author： jhuang
        |##@time：2017/8/22
        """
        if isinstance(searchText, list) is True:
            keys = ','.join(searchText)
            JiraList = []
            searchJQL = 'key in (%s)' % (keys)
            searchText = searchJQL
            logger.debug('jira搜索:%s' % (searchJQL))

        issues = self.jira.search_issues(searchText)

        arrays = []
        attachmentList = []
        for issue in issues:
            dic = {}
            dic['jira_name'] = issue.key
            dic['jira_summary'] = issue.fields.summary
            dic['environment'] = issue.fields.environment
            dic['jira_status'] = issue.fields.status.name
            dic['jira_status_id'] = issue.fields.status.id
            dic['description'] = issue.fields.description
            dic['issue_type'] = issue.fields.issuetype.name
            # 获取修复版本
            str_fix_version = ''
            for fixVersion in issue.fields.fixVersions:
                str_fix_version = str_fix_version + fixVersion.name + ','
            dic['str_fix_version'] = str_fix_version[:-1]
            dic['reporter'] = str(issue.fields.reporter)  # 报告人
            dic['reporter_email'] = str(issue.fields.reporter.emailAddress)  # 报告人邮箱
            dic['assignee_email'] = str(issue.fields.assignee.emailAddress)  # 经办人邮箱
            dic['assignee'] = str(issue.fields.assignee)  # 经办人

            dic['status'] = str(issue.fields.status)

            dic['issue_url'] = '%s/browse/%s' % (self.jira_server_url, issue.key)

            theIssue = self.jira.issue(issue.key)
            #               logger.info ('获取附件信息:%s' %(theIssue.fields.attachment))
            for attachment in theIssue.fields.attachment:
                attachmentDic = {}
                attachmentDic['id'] = attachment.id
                attachmentDic['filename'] = attachment.filename

                attachmentList.append(attachmentDic)
            logger.debug(attachmentList)
            dic['attachment'] = attachmentList

            arrays.append(dic)
        return arrays

    def jql_search_to_list(self, searchText, searchChildIssue=False, searchRelIssue=False, both=False, maxResult=500):
        """
        |##@函数目的：issue 的高级搜索 结果输出为LIST
        |##@参数说明：affectedVersion ='SRMC-15
        |##@返回值：
        |##@函数逻辑：
        |##@开发人：JHUANG
        |##@时间：
        """
        try:
            logger.debug(searchText)
            lists = []
            issues = self.jira.search_issues(searchText, 0, maxResult)
            n = 0

            for issue in issues:
                pdic = {}

                try:
                    customfield_10800 = issue.fields.customfield_10800
                except:
                    customfield_10800 = ''
                pdic['customfield_10800'] = customfield_10800
                pdic['index'] = n
                pdic['rel_type'] = 'parentIssue'
                pdic['parent_issue_key'] = ''
                pdic['rel_issues'] = ''
                pdic['jira_name'] = str(issue.key)
                parentKey = str(issue.key)
                pdic['jira_summary'] = issue.fields.summary
                pdic['environment'] = issue.fields.environment
                pdic['jira_status'] = issue.fields.status.name
                pdic['jira_statu_id'] = issue.fields.status.id

                pdic['description'] = issue.fields.description
                #                问题类型  缺陷/严重等
                pdic['issue_type'] = issue.fields.issuetype.name
                # 获取修复版本
                str_fix_version = ''
                for fixVersion in issue.fields.fixVersions:
                    str_fix_version = str_fix_version + fixVersion.name + ','
                pdic['str_fix_version'] = str_fix_version[:-1]
                pdic['reporter'] = str(issue.fields.reporter)  # 报告人
                pdic['assignee'] = str(issue.fields.assignee)  # 经办人
                pdic['reporter_email'] = str(issue.fields.reporter.emailAddress)  # 报告人邮箱
                pdic['assignee_email'] = str(issue.fields.assignee.emailAddress)  # 经办人邮箱
                # dic['status'] = str(issue.fields.status)
                #                 for issueLink in  issue.fields.linkedIssues:
                #                     print issueLink
                pdic['issue_url'] = '%s/browse/%s' % (self.jira_server_url, issue.key)
                pdic['created_time'] = str(issue.fields.created).replace('T', ' ')[0:19]
                pdic['updated_time'] = str(issue.fields.updated).replace('T', ' ')[0:19]
                pdic['duedate'] = str(issue.fields.duedate).replace('T', ' ')[0:19]
                pdic['resolution'] = str(issue.fields.resolution)
                pdic['resolutiondate'] = str(issue.fields.resolutiondate).replace('T', ' ')[0:19]

                n += 1

                relIssueList = []
                if both:
                    logger.debug('查询子任务+关联任务...%s' % parentKey)

                    childIssues = self.jira.search_issues(
                        'parent =%s or issue in linkedIssues(%s)' % (parentKey, parentKey))
                    for issue in childIssues:
                        dic = {}
                        dic['index'] = n
                        dic['rel_type'] = 'childIussue+relIssue'
                        dic['parent_issue_key'] = parentKey
                        dic['jira_name'] = str(issue.key)
                        relIssueList.append(str(issue.key))
                        dic['jira_summary'] = issue.fields.summary
                        dic['environment'] = issue.fields.environment
                        dic['jira_status'] = issue.fields.status.name
                        dic['jira_statu_id'] = issue.fields.status.id
                        dic['description'] = issue.fields.description
                        #                问题类型  缺陷/严重等
                        dic['issue_type'] = issue.fields.issuetype.name
                        # 获取修复版本
                        str_fix_version = ''
                        for fixVersion in issue.fields.fixVersions:
                            str_fix_version = str_fix_version + fixVersion.name + ','
                        dic['str_fix_version'] = str_fix_version[:-1]
                        dic['reporter'] = str(issue.fields.reporter)  # 报告人
                        dic['assignee'] = str(issue.fields.assignee)  # 经办人
                        dic['reporter_email'] = str(issue.fields.reporter.emailAddress)  # 报告人邮箱
                        dic['assignee_email'] = str(issue.fields.assignee.emailAddress)  # 经办人邮箱
                        # dic['status'] = str(issue.fields.status)
                        #                 for issueLink in  issue.fields.linkedIssues:
                        #                     print issueLink
                        dic['issue_url'] = '%s/browse/%s' % (self.jira_server_url, issue.key)
                        dic['createdTime'] = str(issue.fields.created).replace('T', ' ')[0:19]
                        dic['updated_time'] = str(issue.fields.updated).replace('T', ' ')[0:19]
                        dic['duedate'] = str(issue.fields.duedate).replace('T', ' ')[0:19]
                        dic['resolution'] = str(issue.fields.resolution)
                        dic['resolutiondate'] = str(issue.fields.resolutiondate).replace('T', ' ')[0:19]

                        n += 1
                        lists.append(dic)

                if searchChildIssue and both == False:

                    logger.debug('查询子任务...%s' % parentKey)
                    childIssues = self.jira.search_issues('parent = %s' % (parentKey))
                    for issue in childIssues:
                        dic = {}
                        dic['index'] = n
                        dic['rel_type'] = 'childIussue'
                        dic['parent_issue_key'] = parentKey
                        dic['jira_name'] = str(issue.key)
                        relIssueList.append(str(issue.key))
                        dic['jira_summary'] = issue.fields.summary
                        dic['environment'] = issue.fields.environment
                        dic['jira_status'] = issue.fields.status.name
                        dic['jira_statu_id'] = issue.fields.status.id
                        dic['description'] = issue.fields.description
                        #                问题类型  缺陷/严重等
                        dic['issue_type'] = issue.fields.issuetype.name
                        # 获取修复版本
                        str_fix_version = ''
                        for fixVersion in issue.fields.fixVersions:
                            str_fix_version = str_fix_version + fixVersion.name + ','
                        dic['str_fix_version'] = str_fix_version[:-1]
                        dic['reporter'] = str(issue.fields.reporter)  # 报告人
                        dic['assignee'] = str(issue.fields.assignee)  # 经办人
                        dic['reporter_email'] = str(issue.fields.reporter.emailAddress)  # 报告人邮箱
                        dic['assignee_email'] = str(issue.fields.assignee.emailAddress)  # 经办人邮箱
                        # dic['status'] = str(issue.fields.status)
                        #                 for issueLink in  issue.fields.linkedIssues:
                        #                     print issueLink
                        dic['issue_url'] = '%s/browse/%s' % (self.jira_server_url, issue.key)
                        dic['createdTime'] = str(issue.fields.created).replace('T', ' ')[0:19]
                        dic['updated_time'] = str(issue.fields.updated).replace('T', ' ')[0:19]
                        dic['duedate'] = str(issue.fields.duedate).replace('T', ' ')[0:19]
                        dic['resolution'] = str(issue.fields.resolution)
                        dic['resolutiondate'] = str(issue.fields.resolutiondate).replace('T', ' ')[0:19]

                        n += 1
                        lists.append(dic)

                if searchRelIssue and both == False:

                    logger.debug('查询相关任务...')
                    childIssues = self.jira.search_issues('issue in linkedIssues(%s)' % (parentKey))
                    for issue in childIssues:
                        dic = {}
                        dic['index'] = n
                        dic['rel_type'] = 'relIssue'
                        dic['parent_issue_key'] = parentKey
                        dic['jira_name'] = str(issue.key)
                        relIssueList.append(str(issue.key))
                        dic['jira_summary'] = issue.fields.summary
                        dic['environment'] = issue.fields.environment
                        dic['jira_status'] = issue.fields.status.name
                        dic['jira_statu_id'] = issue.fields.status.id
                        dic['description'] = issue.fields.description
                        #                问题类型  缺陷/严重等
                        dic['issue_type'] = issue.fields.issuetype.name
                        # 获取修复版本
                        str_fix_version = ''
                        for fixVersion in issue.fields.fixVersions:
                            str_fix_version = str_fix_version + fixVersion.name + ','
                        dic['str_fix_version'] = str_fix_version[:-1]
                        dic['reporter'] = str(issue.fields.reporter)  # 报告人
                        dic['assignee'] = str(issue.fields.assignee)  # 经办人
                        dic['reporter_email'] = str(issue.fields.reporter.emailAddress)  # 报告人邮箱
                        dic['assignee_email'] = str(issue.fields.assignee.emailAddress)  # 经办人邮箱
                        # dic['status'] = str(issue.fields.status)
                        #                 for issueLink in  issue.fields.linkedIssues:
                        #                     print issueLink
                        dic['issue_url'] = '%s/browse/%s' % (self.jira_server_url, issue.key)
                        dic['createdTime'] = str(issue.fields.created).replace('T', ' ')
                        dic['updated_time'] = str(issue.fields.updated).replace('T', ' ')
                        dic['duedate'] = str(issue.fields.duedate).replace('T', ' ')
                        dic['resolution'] = str(issue.fields.resolution)
                        dic['resolutiondate'] = str(issue.fields.resolutiondate).replace('T', ' ')

                        n += 1
                        lists.append(dic)

                pdic['relissues'] = relIssueList
                lists.append(pdic)
            return lists

        except Exception as e:
            logger.exception('异常信息')
            lists = []

    def search_issue(self, searchText):
        '''
        搜索issue列表
        返回结果是jira搜索结果数组
        '''
        searchText = str(searchText).replace(' ', '')
        str1 = 'key = "' + searchText + '" OR text ~ "' + searchText + '"'
        str1 = 'key = "' + searchText + '"'
        str2 = 'summary ~ ' + searchText
        try:
            arrays = self._search_issue(str1)
        except Exception as e:
            logger.exception('异常信息')
            try:
                arrays = self._search_issue(self, str2)
            except Exception as e:
                logger.exception('异常信息')
                arrays = []
                return arrays, str(e)
        return arrays, '1'

    def jql_search(self, searchText, type=0):
        """
        |##@函数目的：issue 的高级搜索
        |##@参数说明：affectedVersion ='SRMC-15
        |##@返回值：type =1 执行原生高级搜索
        |##@函数逻辑：
        |##@开发人：runksun
        |##@时间：2017年2月23日
        """
        r = re.findall('^\w+-\d+$', searchText)
        if r:
            logger.debug('用户输入的纯JIRA号,进行高级搜索格式化...')
            searchText = 'key = "' + r[0] + '" OR text ~ "' + r[0] + '"'
        else:

            logger.debug(searchText)
        try:
            if type == 0:
                arrays = self._search_issue(searchText)
            else:
                return self.jira.search_issues(searchText), type
        except Exception as e:
            logger.exception('异常信息')
            arrays = []
        return arrays, '1'

    def search_issue_status(self, jira_name):
        """
            |##@函数目的：查询issue的状态
            |##@参数说明：jira_name 支持 包含多个key 的list
            |##@返回值：list
            |##@函数逻辑：
            |##@开发人：runksun,jhuang
            |##@时间：2017年1月17日
            JQL高级搜索文档：https://confluence.atlassian.com/jira060/advanced-searching-370704913.html
        """
        # tstart=time.time()
        # 将多个KEY 进行高级搜索，一次查询，速度快
        if isinstance(jira_name, list) is True:
            if len(jira_name) <= 0:
                return None
            keys = ','.join(jira_name)
            JiraList = []
            searchJQL = 'key in (%s)' % (keys)
            print searchJQL

            issues = self.jira.search_issues(searchJQL, 0, 1000)

            for issue in issues:
                dic = {}
                # print issue.key
                dic['key'] = issue.key
                dic['statu'] = issue.fields.status.name
                dic['jira_statu_id'] = issue.fields.status.id

                dic['issuetype'] = issue.fields.issuetype
                dic['assignee'] = str(issue.fields.assignee)  # 经办人
                JiraList.append(dic)
            logger.debug('查询状态完成!')
            return JiraList

        else:
            jira_name = str(jira_name).replace(' ', '')
            str1 = 'key =' + jira_name
            try:
                issue = self.jira.search_issues(str1)
                jira_status = issue[0].fields.status.name
            except:
                jira_status = '状态未知'
            finally:
                return jira_status
