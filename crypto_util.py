# -*- coding: utf-8 -*-
import hashlib
from binascii import b2a_hex, a2b_hex

from Crypto.Cipher import AES


from .db_util import sql_to_list
from .log_util import logger


class StringCrypt():
    """
    |##@函数目的：加密类,字符串加密,无特殊字符,方便存储
    |##@参数说明：
    |##@返回值：
    |##@函数逻辑：
    调用示例:
            pc = StringCrypt('keyskeyskeyskeys')      #初始化密钥
            e = pc.encrypt("00000")
            d = pc.decrypt(e)                     
            logger.info  ( e, d)
            e = pc.encrypt("00000000000000000000000000")
            d = pc.decrypt(e)                  
            logger.info  ( e, d )
    |##@开发人：jhuang
    |##@时间：
    """

    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC

    # 加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext)

    # 解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text.rstrip('\0')


def encrypt_pwd(password):
    """
    |##@函数目的：加密string
    |##@参数说明：
    |##@返回值：
    |##@函数逻辑：
    |##@开发人：runksun
    |##@时间：2017年1月11日
    """
    obj = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
    # 这里密钥key 长度必须为16（AES-128）,
    # 24（AES-192）,或者32 （AES-256）Bytes 长度
    # 目前AES-128 足够目前使用
    length = 16
    count = len(password)
    if count < length:
        add = (length - count)
        for i in range(0, add):
            # \0 backspace
            password = password + ' '

    password_aes = obj.encrypt(password)

    # Pickle dictionary using protocol 0.
    return b2a_hex(password_aes)


def decrypt_pwd(password_aes):
    """
    |##@函数目的：解密password
    |##@参数说明：
    |##@返回值：
    |##@函数逻辑：
    |##@开发人：runksun
    |##@时间：2017年1月4日
    """
    obj = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
    plain_text = obj.decrypt(a2b_hex(password_aes))
    return plain_text.replace(' ', '')


def md5(str1):
    """
    | ##@函数目的: 字符串MD5
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    m = hashlib.md5()
    m.update(str1)
    return m.hexdigest()


def pwd_help(pwd_str, string_crypt, encrypt=False):
    """
    pwd_str 密码字符串
    string_crypt 加密秘钥对象
    encrypt Ture 加密后返回，False 解密返回（如果加密了）
    @author： lanxiong
    @time：2018/10/26
    """
    import re
    re_pwd = re.findall('\^_\^(.*?)\^_\^', pwd_str)

    if encrypt:
        if len(re_pwd) == 1:
            logger.info('已经加密过')
            return [False, pwd_str]
        else:
            logger.info('没有加密过，需要加密存储')
            sql = """
                select hex(aes_encrypt('{}', '{}')) as en_str
            """.format(pwd_str, string_crypt.key)
            mysql_pwd_str = sql_to_list(sql)[0]['en_str']
            pwd_str = '^_^%s^_^' % mysql_pwd_str
            # pwd_str = '^_^%s^_^' % string_crypt.encrypt(pwd_str)
            return [True, pwd_str]
    else:
        logger.info('判断密码是否被加密')
        if len(re_pwd) == 1:
            logger.info('密码被加密，需要解密')
            sql = """
                select aes_decrypt(unhex('{}'), '{}') as de_str
            """.format(re_pwd[0], string_crypt.key)
            pwd_str = sql_to_list(sql)[0]['de_str']
            # pwd_str = string_crypt.decrypt(re_pwd[0])
            return pwd_str
        else:
            logger.info('密码没有被加密')
            return pwd_str