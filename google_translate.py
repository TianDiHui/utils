# -*- coding: utf-8 -*-


from googletrans import Translator

translator = Translator(service_urls=[
    'translate.google.cn', ])


# 'zh-CN','EN'

# 文章伪原创
def art_ai(text):
    data = translator.translate(translator.translate(text, src='zh-CN', dest='EN').text, src='EN',
                                dest='zh-CN').text
    return data
