# -*- coding: utf-8 -*-
import re

from cpms_home.utils.db_util import sql_to_list


class EchartJS():
    """
    | ##@函数目的: 将数据转换为EACHARTJS 的各种数据结构
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """

    def __init__(self):
        pass

    def sql_to_pie_dict(self, sql, name=''):
        """
        只允许传入两个值
        # {
        #     tooltip: {
        #         trigger: 'item',
        #         formatter: "{a} <br/>{b} : {c} ({d}%)"
        #     },
        #
        #     series: [
        #         {
        #             name: '访问来源',
        #             type: 'pie',
        #             data: [
        #                 {value: 335, name: '直接访问'},
        #                 {value: 310, name: '邮件营销'},
        #                 {value: 234, name: '联盟广告'},
        #                 {value: 135, name: '视频广告'},
        #                 {value: 1548, name: '搜索引擎'}
        #             ]
        #         }
        #     ]
        # }"""
        rows_return = []
        dict = {
            'tooltip': {
                'trigger': 'item',
                'formatter': "{a} <br/>{b} : {c} ({d}%)"
            },
            'toolbox': {
                'show': "true",
                'feature': {
                    'mark': '{show: true}',
                    'dataView': '{show: true, readOnly: false}',
                    'magicType': "{show: true, type: ['line', 'bar','pie']}",
                    'restore': '{show: true}',
                    'saveAsImage': '{show: true}'
                }
            },
            'calculable': 'true',
            'series': [
                {
                    'name': name,
                    'type': 'pie',
                    'data': rows_return
                }
            ]

        }

        rows = sql_to_list(sql, None, True)

        if len(rows[0]) != 2:
            return '列数不符合!'

        zhPattern = re.compile(u'[\u4e00-\u9fa5]+')

        for rowid, rowkey in rows[0].items():
            if isinstance(rowkey, float) or isinstance(rowkey, int):
                for rows_one in rows:
                    nu = 0
                    one = {}
                    for value, key in rows_one.items():
                        if nu == 0:
                            one['value'] = key
                        elif nu == 1:
                            one['name'] = key
                        nu += 1

                    rows_return.append(one)

                return dict

            elif zhPattern.search(u'%s' % rowkey) or rowkey.isalpha():
                for rows_one in rows:
                    nu = 0
                    one = {}
                    for value, key in rows_one.items():
                        if nu == 0:
                            one['name'] = key
                        elif nu == 1:
                            one['value'] = key
                        nu += 1
                    rows_return.append(one)

                return dict
            else:
                return '查询内容不符合图形要求!'

    def sql_semi_automatic(self, sql, name=''):
        """
        手动标记value与name，入参多个值
        :param sql:
        :param name:
        :return:
        liww
        """

        rows = sql_to_list(sql, None, True)

        #计算总计
        total = 0.0
        for row in rows:
            if row['value'] != None:
                total  += float(row['value'])


        dict = {
            'title': {
                'subtext': '合计:%.2f' %total,
                'x': 'right',
                'top': 20,
                'subtextStyle': {
                     'color': '#4f5555'
                       }
            },
            'tooltip': {
                'trigger': 'item',
                'formatter': "{a} <br/>{b} : {c} ({d}%)"
            },
            'toolbox': {
                'show': "true",
                'feature': {
                    'mark': '{show: true}',
                    'dataView': '{show: true, readOnly: false}',
                    'magicType': "{show: true, type: ['line', 'bar','pie', 'stack', 'tiled']}",
                    'restore': '{show: true}',
                    'saveAsImage': '{show: true}'
                }
            },
            'calculable': 'true',
            'series': [
                {
                    'name': name,
                    'type': 'pie',
                    'data': rows
                }
            ]

        }
        return dict

    def sql_to_category(self, sql):
        """
            app.config = {
        rotate: 90,
        align: 'left',
        verticalAlign: 'middle',
        position: 'insideBottom',
        distance: 15,
    };


    var labelOption = {
        normal: {
            show: true,
            position: app.config.position,
            distance: app.config.distance,
            align: app.config.align,
            verticalAlign: app.config.verticalAlign,
            rotate: app.config.rotate,
            formatter: '{c}  {name|{a}}',
            fontSize: 16,
            rich: {
                name: {
                    textBorderColor: '#fff'
                }
            }
        }
    };

    option = {
        xAxis: [
            {
                type: 'category',
                axisTick: {show: false},
                data: ['2012', '2013', '2014', '2015', '2016']
            }
        ],
        yAxis: [
            {
                type: 'value'
            }
        ],
        series: [
            {
                name: 'Forest',
                type: 'bar',
                barGap: 0,
                label: labelOption,
                data: [320, 332, 301, 334, 390]
            },
            {
                name: 'Steppe',
                type: 'bar',
                label: labelOption,
                data: [220, 182, 191, 234, 290]
            },
            {
                name: 'Desert',
                type: 'bar',
                label: labelOption,
                data: [150, 232, 201, 154, 190]
            },
            {
                name: 'Wetland',
                type: 'bar',
                label: labelOption,
                data: [98, 77, 101, 99, 40]
            }
        ]
    };
        :return:
        """

        rows = sql_to_list(sql, None, True)

        projects_list = []
        department_list = []
        series = []
        department_projects_dict = {}
        projects_department_dict = {}
        department_man_hour_dict = {}
        for row in rows:
            if row['xiangmu'] in projects_list:
                pass
            else:
                projects_list.append(row['xiangmu'])

            if row['bumen'] in department_list:
                pass
            else:
                department_list.append(row['bumen'])

            if projects_department_dict.get(row['xiangmu']):
                projects_department_dict[row['xiangmu']][row['bumen']] = row['gongshizongji']

            else:
                projects_department_dict[row['xiangmu']] = {}
                projects_department_dict[row['xiangmu']][row['bumen']] = row['gongshizongji']

        for projects_one in projects_list:
            for department_one in department_list:

                if department_man_hour_dict.get(department_one):
                    pass
                else:
                    department_man_hour_dict[department_one] = []

                if projects_department_dict[projects_one].get(department_one):
                    department_man_hour_dict[department_one].append(
                        projects_department_dict[projects_one][department_one])
                else:
                    department_man_hour_dict[department_one].append(0)

        for ver, key in department_man_hour_dict.items():
            dict_template_fragment = {
                "name": ver,
                "type": 'bar',
                "barGap": 0,
                "label": "labelOption",
                "data": key
            }
            series.append(dict_template_fragment)

        dict_template = {
            "app.config": {
                "rotate": 90,
                "align": 'left',
                "verticalAlign": 'middle',
                "position": 'insideBottom',
                "distance": 15,
            },
            "var labelOption": {
                "normal": {
                    "show": "true",
                    "position": "app.config.position",
                    "distance": "app.config.distance",
                    "align": "app.config.align",
                    "verticalAlign": "app.config.verticalAlign",
                    "rotate": "app.config.rotate",
                    "formatter": '{c}  {name|{a}}',
                    "fontSize": 16,
                    "rich": {
                        "name": {
                            "textBorderColor": '#fff'
                        }
                    }
                }
            },

            "option": {
                "xAxis": [
                    {
                        "type": 'category',
                        "axisTick": {"show": "false"},
                        "data": projects_list
                    }
                ],
                "yAxis": [
                    {
                        "type": 'value'
                    }
                ],
                "series": series
            }}

        return dict_template
