# # -*- coding: utf-8 -*-
# 
# import json
# import os
# import socket
# import threading
# from time import sleep
# import time
# 
# from dwebsocket.decorators import accept_websocket
# 
# logger = logging.getLogger('django')
# from comUtil import get_except
# from httpUtil import HttpClass
# from stringUtil import get_uuid, time_to_db, get_stamp_now, \
#     dbtime_to_timestamp
# from dbUtil import sql_exec
# from SRMCenter.models.models import WebsocketMsg, WebsocketMsgPid
# 
# 
# mutex = threading.Lock()
# 
# 
# def initMsgQueue():
#     """
#     | ##@函数目的: 清理消息队列
#     | ##@参数说明：https://github.com/duanhongyi/dwebsocket
#     | ##@返回值：
#     | ##@函数逻辑：
#     | ##@开发人：jhuang
#     | ##@时间：
#     """  
#     logger.debug('初始化消息队列...')
#     WebsocketMsgPid.objects.all().delete()
#     WebsocketMsg.objects.all().delete()
# #     threading.Thread(target=queryMsgQueue).start()       
# 
# 
# 
# def websocketServer_SendMsg(msgtype,msg):
# #     logger.debug('提交websocket消息到队列：%s' %(msg))
#     WebsocketMsg(msg=msg,type=msgtype,msg_id=get_uuid(),send_time=time_to_db()).save()
# 
# 
# 
# def queryMsgQueue():
#     '''
#     检查是否有消息需要发送
#     '''
#     mutex.acquire()
#     logger.debug('监控websocket消息队列...')
#     while 1:
#         oWebsocketMsgs=WebsocketMsg.objects.all()
#         for r in oWebsocketMsgs:
#             msgtype=r.type
#             msg=r.msg
#             msg_id=r.msg_id
#             send_time= str(r.send_time )
# #             print send_time
#             t2=dbtime_to_timestamp(send_time)
# #             print t2
# #             print get_stamp_now()
#             oWebsocketMsgPids2=WebsocketMsgPid.objects.filter(msg_id=msg_id)
#             if get_stamp_now()-t2>60*1:
#                 r.delete()
#                 oWebsocketMsgPids2.delete()
# #                 logger.debug('消息已经过期，清理消息...(msg_id:%s)'%(msg_id))
#                 
#            
#             oWebsocketMsgPids=WebsocketMsgPid.objects.filter(msg_id=msg_id,pid=os.getpid())
#             if len(oWebsocketMsgPids)>0:
#                 pass
# #                 logger.debug('已经过，不在发送...')
# #                 if len(oWebsocketMsgPids2)>=8:
# #                     logger.debug('全部发送完成，清理消息...(msg_id:%s)'%(msg_id))
# #                     oWebsocketMsgPids2.delete()
# #                     WebsocketMsgPid.objects.filter(msg_id=msg_id).delete()
#                     
#             else:
#                 sql_exec('insert into websocket_msg_pid  (msg_id,pid) values(%s,%s)',[msg_id,os.getpid()],False)
#                 _websocketServer_SendMsg(msgtype,msg)
# 
#         sleep(5)
#         
# 
# 
# 
# 
# 
# 
# 
# clients = []
# # @accept_websocket
# def websocketServer(request):
#     """
#     | ##@函数目的: 开启一个websocke服务
#     | ##@参数说明：https://github.com/duanhongyi/dwebsocket
#     | ##@返回值：
#     | ##@函数逻辑：
#     | ##@开发人：jhuang
#     | ##@时间：
#     """  
# #     logger.debug('开启websocket服务...')
#     try:
#         if request.is_websocket:
#             clients.append(request.websocket)
#             for message in request.websocket:
#                 for client in clients:
#                     if message!=None:
#                         client.send(message)
#     except Exception as e:
#             clients.remove(request.websocket)
#             logger.error('uwebsocket 通道异常 :%s' %(get_except(e)))
#             # logger.info  (  {0}'.format(ex))
#     finally:
#         pass
# 
#        
# 
# 
# 
#       
# # 向客户端推消息
# def _websocketServer_SendMsg(msgtype,msg):
#     msgdic={}
#     msgdic['msgType'] = unicode(msgtype).encode('UTF-8')
#     msgdic['msg'] = unicode(msg).encode('UTF-8')
#     msg=json.dumps(msgdic, ensure_ascii=False)
#     if len(clients)<=0 :
#             return False
# #         logger.debug('发送websocket消息，失败：无客户端连接！')
#     for client in clients:
#         try:
# #             logger.debug('发送websocket消息：%s' %(msg))
#             client.send(msg)
#         except Exception , e:            
#             logger.error( u'websocket发消息:{0} 出现异常 --> %s'%(get_except(e)))
#             
#   
# 
# 
#             
# 
#             
# 
#   


