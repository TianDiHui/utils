# -*- coding: utf-8 -*-
import datetime
import traceback

logger = logging.getLogger('django')
from django.core.exceptions import ObjectDoesNotExist
from django.forms import model_to_dict

from ..models.models import SysErrorCode


# 调用方法
# GetException(e,logger).get_except() #捕获异常，记录到指定日志句柄
# GetException(e,logger).raise_except() #往上抛出异常


class GetException(object):
    def __init__(self, e, logger_handle=logger):
        self.__e = e
        self.__error = None  # 异常错误摘要
        self.__error_code = None  # 异常错误编码
        self.__error_detail = None  # 异常的详情
        self.__err_text = None  # 异常的详情
        self.__error_html = None  # 异常的详情
        self.explain = None  # 异常的说明
        self.logger_handle = logger_handle

    def get_e(self):
        return self.__e

    def raise_except(self, explain='异常'):
        """
        向上抛出异常

        :param param1: this is a first param
        :param param2: this is a second param
        :returns: this is a description of what is returned
        :raises keyError: raises an exception
        @author： jhuang
        @time：23/07/2018
        """
        self.except_text = self.get_except()

        raise Exception('%s\n细节：%s' % (explain, self.except_text))

    def get_except(self, error_detail=True, error_html=False, write_log=True):
        """
        | ##@函数目的: 获取异常,并打印异常日志
        | ##@参数说明：
        | ##@返回值：字典类型
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        self.__error = str(self.__e).decode('utf-8', errors='ignore')
        # self.__error =self. __e.message.decode('utf-8', errors='ignore')
        # self.__error =self. __e.message#某些情况e没有 e.message属性,e.message 有时候非字符串主要需要字符串
        self.__error_detail = str(traceback.format_exc()).decode('utf-8', errors='ignore')  # 追溯信息
        arrays = [self.__error, self.__error_detail]
        self.__error_code = datetime.datetime.now().strftime('%d%H%M%S')
        self.__err_text = '错误[%s]：%s' % (self.__error_code, self.__error)
        if isinstance(self.__e, CenboomhException):
            self.__error_code = str(getattr(self.__e, 'error_code', self.__error_code)) + '-' + self.__error_code
            # self.__err_text = '错误[%s]：%s' % (self.__error_code, self.__error)
            self.__err_text = """
            ^-^CenboomhException^-^{{"error_code":"{error_code}",
                "summary":"{summary}", 
                "detail":"{detail}",
                "solution":"{solution}",
                "wiki_link":"{wiki_link}"}}^-^CenboomhException^-^""".format(
                error_code=self.__error_code,
                summary=self.__error,
                detail=self.__e.detail,
                solution=self.__e.solution,
                wiki_link=self.__e.wiki_link or ''
            )

        self.__error_html = '<span style="color:#FF5722;padding-left:5px;">【错误】</span>%s<br><hr><span style="color:#000;">' % (
            self.__error)
        if write_log:
            self.logger_handle.exception('错误(error:%s)' % self.__error_code)
        if error_detail is False:
            return self.__error
        else:
            if error_html:
                return self.__error_html
            else:
                return self.__err_text






class CenboomhException(Exception):
    def __init__(self, error_source=None, **kwargs):
        self.__dict__.update(kwargs)
        self.error_source = error_source

    def __str__(self):
        # msg = json.dumps(self.__dict__, ensure_ascii=False, encoding='UTF-8')
        msg = """{}, 错误日志: {}.""".format(self.summary, self.error_source)
        return """{}""".format(msg)


def raise_cbh_exception(error_code, error_source=None):
    try:
        obj_err = SysErrorCode.objects.get(error_code=error_code)
        kwargs = model_to_dict(obj_err, fields=[field.name for field in obj_err._meta.fields])
        if error_source:
            error_source = str(error_source).decode('utf-8', errors='ignore')
            error_source = error_source.replace('	','')
            error_source = error_source.replace('"',"'")
            error_source = error_source.replace('\\',"")
        raise CenboomhException(error_source, **kwargs)
    except ObjectDoesNotExist:
        raise Exception('该错误码不存在，error_code=%s' % error_code)