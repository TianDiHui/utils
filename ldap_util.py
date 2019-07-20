# -*- coding: utf-8 -*-


import ldap

logger = logging.getLogger('django')


class LdapClass():
    def __init__(self, ldap_host, base_dn):
        """
        | ##@函数目的: 初始化
        | ##@参数说明：
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        # base_dn='ou=users,dc=tonghe,dc=com'
        self.ldap_host = ldap_host  # '192.168.219.42'
        # logger.debug(ous)
        # self.ous=ous#['','ou=pwc','ou=tjh','ou=tjm','ou=tjxn','ou=tpv','ou=zjh-tpv','ou=zjyy','ou=practice','ou=cs-office']
        self.base_dn = base_dn  # "dc=tonghe,dc=com"

        self.oladp = ldap.initialize('ldap://%s' % (self.ldap_host))
        self.oladp.protocol_version = ldap.VERSION3
        logger.debug(u'LDAP_Init->ldap.VERSION3 = %s' % (self.oladp.protocol_version))

    def login(self, username, pwd):
        """
        | ##@函数目的: 获取用户信息，
        | ##@参数说明： ladp实例化对象
        | ##@返回值：login_success=TRUE 登陆成功 ，userInfo_dic 包含用户信息
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        # 用户是否登陆成功
        login_success = False
        userInfo_dic = {}
        logger.debug(u'查询用户信息...')
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None
        searchFilter = "cn=" + username
        ldap_result_id = self.oladp.search(self.base_dn, searchScope, searchFilter, retrieveAttributes)
        result_type, result_data = self.oladp.result(ldap_result_id, 0)
        print result_data, result_type
        if result_type == ldap.RES_SEARCH_ENTRY:

            username = str(result_data[0][1]['cn'][0]).replace(' ', '')
            email = result_data[0][1]['mail'][0]

            sn = str(result_data[0][1]['sn'][0]).replace(' ', '')  # 名
            try:
                givenName = str(result_data[0][1]['givenName'][0]).replace(' ', '')  # 姓
            except:
                givenName=sn
            logger.debug('%s%s' % (givenName[0:4], sn[0:3]))
            if givenName != '':
                if givenName[0:4] == sn[0:3]:
                    ch_name = sn
                else:
                    ch_name = str('%s%s' % (givenName, sn)).replace(' ', '')
            else:
                ch_name = sn
            try:
                ch_name = result_data[0][1]['displayName'][0]
            except:
                ch_name =sn

            userInfo_dic = {'username': username, 'email': email, 'givenName': givenName, 'sn': sn, 'ch_name': ch_name}
            logger.debug(userInfo_dic)
            logger.debug('验证用户密码...')
            DN = result_data[0][0]
            try:
                self.oladp.simple_bind_s(DN, pwd)
                login_success = True
            except:
                logger.debug('用户名和密码验证失败！')
                login_success = False
            return login_success, userInfo_dic
        else:
            return login_success, userInfo_dic

    def login_admin(self, username, password):
        """
        #ldap_host:"ldap://192.168.10.11:389"
        #base_dn = "dc=tonghe,dc=com"
        :param username: "cn=Manager,dc=tonghe,dc=com"
        :param password:
        :return:
        liww
        """
        # self.ldap_conn = ldap.initialize(self.ldap_host)
        self.oladp.simple_bind(username, password)

    def query_user(self, attr_type, value):
        """
        查找用户基本信息
        attr_type:属性类型，如：uid,cn
        value:属性值，如：jhuang

        """
        conn = self.oladp
        conn.protocal_version = ldap.VERSION3
        serach_cope = ldap.SCOPE_SUBTREE
        retrieve_attributes = None
        search_filter = attr_type + "=" + str(value)
        ldap_result_id = conn.search(self.base_dn, serach_cope, search_filter, retrieve_attributes)
        result_type, result_data = conn.result(ldap_result_id)
        return result_data

    def ldap_user_serach(self, attr_type, value):
        """
        查找用户
        attr_type:属性类型，如：uid,cn
        value:属性值，如：wwu
        wwu
        """
        conn = self.oladp
        conn.protocal_version = ldap.VERSION3
        serach_cope = ldap.SCOPE_SUBTREE
        retrieve_attributes = None
        search_filter = attr_type + "=" + str(value)
        try:
            ldap_result_id = conn.search(self.base_dn, serach_cope, search_filter, retrieve_attributes)
            result_type, result_data = conn.result(ldap_result_id)
            if not result_data:
                print "无法找到用户！"
                return False, []
            else:
                for i in result_data:
                    dn_name = i[0]
                    dn_attr = i[1]
                print "dn:%s" % (dn_name)
                for k in dn_attr:
                    print "%s:%s" % (k, dn_attr[k])
                return True
        except ldap.LDAPError, e:
            raise e

    def ldap_user_add(self, base_dn, user_passwd, nick, uidNumber):
        """
        添加用户
        base_dn: uid=wwu1,ou=practice,ou=users,dc=tonghe,dc=com
        """
        dn_list = base_dn.split(',')
        u_id = str(dn_list[0].split('=')[1])
        add_record = [('objectclass', ['organizationalPerson', 'inetOrgPerson', 'posixAccount']),
                      ('cn', ['%s' % (u_id)]),
                      ('sn', ['%s' % (str(nick))]),
                      ('userpassword', ['%s' % (str(user_passwd))]),
                      ('uidNumber', ['%s' % (str(uidNumber))]),
                      ('gidNumber', ['0']),
                      ('homeDirectory', ['/opt/ftpsite/%s' % (u_id)]),
                      ('mail', ['%s@cenboomh.com' % (u_id)])
                      ]
        try:
            result = self.oladp.add_s(base_dn, add_record)
        except ldap.LDAPError, e:
            raise e
        else:
            if result[0] == 105:
                return True, []
            else:
                return False, result[1]

    def ladp_getuser_dn(self, uid):
        """
        返回用户所在的dn
        uid:用户名称，如:wwu
        wwu
        """
        conn = self.oladp
        conn.protocal_version = ldap.VERSION3
        serach_cope = ldap.SCOPE_SUBTREE
        retrieve_attributes = None
        search_filter = str("uid=%s" % uid)
        try:
            ldap_result_id = conn.search(self.base_dn, serach_cope, search_filter, retrieve_attributes)
            result_type, result_data = conn.result(ldap_result_id)
            if not result_data:
                print "无法找到用户！"
                return False
            else:
                for i in result_data:
                    dn_name = i[0]
                return dn_name
        except ldap.LDAPError, e:
            raise e


    def ldap_lalter_office_info(self, uid, newuid, type=None, passwd='', mail=''):
        """
        信息修改
        :param uid:
        :return:
        """
        user_dn = self.ladp_getuser_dn(uid)
        conn = self.oladp

        try:
            if type == 'dimission':
                if user_dn != False:
                    conn.modify_s(user_dn, [(ldap.MOD_REPLACE, 'userPassword', '{SHA}fCIvspJ9goryL1khNOiTJIBjfA0=')])
                    conn.rename_s(user_dn, 'uid=%s' % newuid)
            elif type == 'userdelete':
                #self.ldap_user_delete(user_dn)
                if user_dn != False:
                    conn.rename_s(user_dn, 'uid=%s' % (uid + '_shut'))
            elif type == 'useradd':
                uid_s = uid + '_shut'
                user_dn = self.ladp_getuser_dn(uid_s)
                if user_dn != False:
                    conn.rename_s(user_dn, 'uid=%s' % newuid)
                else:
                    return False
            else:
                if passwd != None:
                    conn.modify_s(user_dn, [(ldap.MOD_REPLACE, 'userPassword', str(passwd))])
                conn.modify_s(user_dn, [(ldap.MOD_REPLACE, 'mail', str(mail))])
                conn.modify_s(user_dn, [(ldap.MOD_REPLACE, 'cn', str(newuid))])
                conn.rename_s(user_dn, 'uid=%s' % newuid)
            # conn.unbind_s()
            return True
        except ldap.LDAPError, e:
            print("%s 失败，原因: %s" % (uid, str(e)))
            return False

    def ldap_adduser_to_group(self, cn_name, user_dn, ou_name=[]):
        """
        添加用户到ou
        ou_name: 组织单元列表，如['groups','jira']
        cn_name: 组名,如：develps,login
        users:用户列表，如：['wwu','wwu1']
        注函数中定义的参数modlist可以接受多个参数列表，其中：
        MOD_ADD: 如果属性存在，这个属性可以有多个值，那么新值加进去，旧值保留
        MOD_DELETE ：如果属性的值存在，值将被删除
        MOD_REPLACE ：这个属性所有的旧值将会被删除，这个值被加进去
        举例：
         [( ldap.MOD_ADD, 'memberUid', 'user1' ),
        ( ldap.MOD_DELETE, 'memberUid', 'user3')]
        wwu
        """
        oulist = []
        for i in ou_name:
            oulist.append('ou=%s' % i)
        try:
            conn = self.oladp
            modifyDN = str("cn=%s,%s,%s" % (cn_name, ','.join(oulist), self.base_dn))
            conn.modify_s(modifyDN, [(ldap.MOD_ADD, 'uniqueMember', user_dn)])
            # conn.unbind_s()
            return True
        except ldap.LDAPError, e:
            print("%s 添加失败，原因: %s" % (cn_name, str(e)))
            return False

    def ldap_deleteuser_from_group(self, cn_name, user_dn, ou_name=[]):
        """
        删除ou内的条目
        cn_name: 组名,如：develps,login
        ou_name: 组织单元列表，如['groups','jira']
        users:用户列表，如：['wwu','wwu1']
        """
        oulist = []
        for i in ou_name:
            oulist.append('ou=%s' % i)
        try:
            conn = self.oladp
            modifyDN = "cn=%s,%s,%s" % (cn_name, ','.join(oulist), self.base_dn)
            conn.modify_s(modifyDN, [(ldap.MOD_DELETE, 'uniqueMember', user_dn)])
            # conn.unbind_s()
            return True
        except ldap.LDAPError, e:
            print("%s 删除失败，原因: %s" % (cn_name, str(e)))
            return False

    def ldap_user_delete(self, user_dn):
        """
        user_dn:uid=wwu1,ou=practice,ou=users,dc=tonghe,dc=com:
        """
        try:
            conn = self.oladp
            result = conn.delete_s(user_dn)
        except ldap.LDAPError as e:
            raise e
        else:
            if result[0] == 107:
                return True, []
            else:
                return False, result[1]
