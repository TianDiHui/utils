# -*- coding: utf-8 -*-
import os

from json2xls import Json2Xls
import requests


class Json2XlsFix(Json2Xls):
    def __get_json(self):
        data = None
        try:
            data = self.json_loads(self.json_data)
        except:
            if os.path.isfile(self.json_data):
                with open(self.json_data, 'r') as source:
                    try:
                        data = self.json_loads(source.read().decode('utf-8').replace('\n', ''))
                    except:
                        source.seek(0)
                        data = [self.json_loads(line.decode('utf-8')) for line in source]
            else:
                if os.path.isfile(self.headers):
                    with open(self.headers) as headers_txt:
                        self.headers = self.json_loads(headers_txt.read().decode('utf-8').replace('\n', ''))
                elif isinstance(self.headers, basestring):
                    self.headers = self.json_loads(self.headers)
                try:
                    if self.method.lower() == 'get':
                        resp = requests.get(self.json_data,
                                            params=self.params,
                                            headers=self.headers)
                        data = resp.json()
                    else:
                        if isinstance(self.post_data, basestring) and os.path.isfile(self.post_data):
                            with open(self.post_data, 'r') as source:
                                self.post_data = self.json_loads(source.read().decode('utf-8').replace('\n', ''))
                        if not self.form_encoded:
                            self.post_data = self.json_dumps(self.post_data)
                        resp = requests.post(self.json_data,
                                             data=self.post_data, headers=self.headers)
                        data = resp.json()
                except Exception as e:
                    print e
        return data
