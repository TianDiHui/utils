# -*- coding: utf-8 -*-
from db_util import Sql2List, sql_to_list


class EasyUI(object):
    def __init__(self):
        pass



    def create_grid_cell_property_dict(self):
        # 创建一个easyui grid 单元格对象，前台拿这个对象进行单元格渲染
        self.grid_cell_dict = {}
        self.grid_cell_dict['bgcolor'] = ''  ##5FB878
        self.grid_cell_dict['color'] = ''  ##01AAED
        self.grid_cell_dict['title'] = ''  # 连云港第一人民医院
        self.grid_cell_dict['value'] = ''  # 连
        self.grid_cell_dict['desc'] = ''  # 连云港第一人民医院，单元格的描述

    def list_2_grid_pagin(self, lst):
        """
       列表切片到grid


        :returns: 符合grid的分页格式的数据
        :raises keyError: raises an exception
        @author： jhuang
        @time：8/31/2018
        """

        row_total = len(lst)
        dict_grid = {}
        dict_grid['total'] = row_total
        #dict_grid['rows'] = lst[self.page_start_row:self.page_end_row - 1]
        dict_grid['rows'] = lst[self.page_start_row:self.page_end_row]
        return dict_grid

    def get_pagin_param(self, request, method='GET'):
        """
        获取grid分页参数

        :param param1: this is a first param
        :param param2: this is a second param
        :returns: this is a description of what is returned
        :raises keyError: raises an exception
        @author： jhuang
        @time：8/31/2018
        """
        if len(request.POST)>0:
            self.page = request.POST.get('page', 1)
            self.page_row_size = request.POST.get('rows', 20)
        else:
            self.page = request.GET.get('page', 1)
            self.page_row_size = request.GET.get('rows', 20)


        self.page = int(self.page)
        self.page_row_size = int(self.page_row_size)
        self.page_start_row = (self.page - 1) * self.page_row_size  # 0,,10
        self.page_end_row = (self.page) * self.page_row_size  # 10,20

    def sql_2_grid_pagin(self, sql):
        """
        提交一个查询，按指定条件自动grid分页
        # 3行代码实现easyui grid后台分页查询，返回rows是分页查询后的数据
        # 后台开发不需关心分页入参，入参前台控制；参数:sql:只需写你需查的数据即可）
        easyui = EasyUI()
        easyui.get_pagin_param(request)
        rows = easyui.sql_2_grid_pagin(sql)
        return response_json(rows)


        :param request: http请求对象
        :param sql：需要查询数据的SQL，不需要考虑分页
        :returns: 符合grid的分页格式的数据
        :raises keyError: raises an exception
        @author： jhuang
        @time：8/31/2018
        """
        mysql_limit_sql = "limit {page_start_row},{page_row_size}".format(page_start_row=self.page_start_row,
                                                                          page_row_size=self.page_row_size)
        sql_total = """select count(1) as total from (%s)  aa""" % (sql)
        sql2list = Sql2List()
        row_total = sql2list.sql_to_list(sql_total)[0]['total']

        sql_pagin = """select * from (%s) aa  %s""" % (sql, mysql_limit_sql)
        pagin_rows = sql2list.sql_to_list(sql_pagin)
        dict_grid = {}
        dict_grid['total'] = row_total
        dict_grid['rows'] = pagin_rows
        sql2list.close()
        return dict_grid

    def tree_recursive(self, data, depth=3, show_all=False):
        """
        easyui_tree recurisve 递归
        :param param1: this is a first param
        :param param2: this is a second param
        :returns: this is a description of what is returned
        :raises keyError: raises an exception
        @author： jhuang
        @time：12/05/2018
        @amend:liww @time:11/09/2018
        """
        # 判断循环次数为len(data）

        for s in range(depth):

            a = 0  # 记录for循环次数
            for i in range(0, len(data))[::-1]:
                # type(data)
                a = a + 1  # 当前第一次循环
                b = 0  # 判断是否存在子节点，存在赋值为1，不存在为0
                for j in data:
                    if data[i]['id'] == j['pid']:  # 当前I 是子节点，当存在子节点时b=1退出当前for循环进入下一次循环
                        b = 1
                        # print i['id']
                        continue
                if b == 0:  # 当b==0也就是i这条数据没有子节点时把它加入到父节点中
                    for h in data:
                        try:
                            if h['id'] == data[i]['pid']:  # 将作为子节点的I加入到其父节点，是否存在父节点,这里I是一个子节点
                                if h.has_key('children'):
                                    h['children'].append(data[i])  # 如果当前的父节点存在children这个键，直接append（i）
                                    # h['children_id_list'].append(i['id'])  # 如果不存在则把新建children键，此键类型为list，并把当前数据加入到父节点中

                                else:
                                    h['children'] = []
                                    # h['children_id_list'] = []
                                    h['children'].append(data[i])  # 如果不存在则把新建children键，此键类型为list，并把当前数据加入到父节点中
                                    # h['children_id_list'].append(i['id'])  # 如果不存在则把新建children键，此键类型为list，并把当前数据加入到父节点中
                                del data[i]
                                i = i - 1
                                # del data[a - 1]  # 删除当前数据
                                # print data
                                break
                                # continue
                        except:
                            pass
        # if show_all:
            # dic = {}
            # dic['text'] = '全部'
            # dic['pid'] = ''
            # dic['id'] = ''
            # data.insert(0, dic)
        return data
