# -*- coding: utf-8 -*-
import os
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext, Template
from django.utils.encoding import smart_str, smart_unicode
import hashlib
from xml.etree import ElementTree as etree
import getinfo
from wechat_sdk import WechatBasic
from wechat_sdk.exceptions import ParseError
from wechat_sdk.messages import TextMessage
import json
'''
WECHAT_TOKEN = 'jcgalileo'
AppID = 'wx4b7943f082770e22'
AppSecret = '60186ab20d8e44bf2e7c496a9e7a34a1'
'''
WECHAT_TOKEN = 'jcgalileo2'
AppID = 'wx5a13781f1ae1b5be'
AppSecret = 'd4624c36b6795d1d99dcf0547af5443d'

MY_OPENID = 'o2cILxORC3vAZHOMrCgcfeixBT2w'

fp_tmp = open('log_tmp.txt','a+')
fp_uid = open('log_uid.txt','a+')

# 实例化 WechatBasic
wechat_instance = WechatBasic(
    token=WECHAT_TOKEN,
    appid=AppID,
    appsecret=AppSecret
)

light_flag = 0
detect_flag = 0

@csrf_exempt
def index(request):
    global light_flag
    global detect_flag
    if request.method=='GET':
        response=HttpResponse(checkSignature(request))
        return response
    else:
        xmlstr = smart_str(request.body)
        xml = etree.fromstring(xmlstr)
        temprature = xml.find('temprature')
        light = xml.find('light')
        dangerous = xml.find('dangerous')
        if temprature != None:
            fp_tmp.seek(0,2)
            fp_tmp.write(temprature.text)
            #if temprature.text == '1234':
            #    fp = open('galileo.jpg','rb')	
            #    upload_info = wechat_instance.upload_media("image", fp)
            #    image_id = upload_info['media_id']
            #    wechat_instance.send_image_message(MY_OPENID, image_id)
            return HttpResponse("0")
        if light != None:
            return HttpResponse(str(light_flag))
        if dangerous != None and detect_flag == 1:
            fp = open('galileo_dangerous.jpg','rb')	
            upload_info = wechat_instance.upload_media("image", fp)
            image_id = upload_info['media_id']
            wechat_instance.send_text_message(MY_OPENID, u"监控报警!请注意!")
            wechat_instance.send_image_message(MY_OPENID, image_id)
            return HttpResponse("ok recieved!")
        #获取open_id
        #open_id = xml.find('FromUserName')
        #if open_id != None:
        #    fp_uid.seek(0,2)
        #    fp_uid.write(open_id.text)
        #    fp_uid.write('\n')
        
        # 解析本次请求的 XML 数据
        try:
            wechat_instance.parse_data(data=request.body)
        except ParseError:
            return HttpResponseBadRequest('Invalid XML Data')
 
        # 获取解析好的微信请求信息
        message = wechat_instance.get_message()
 
        # 关注事件以及不匹配时的默认回复
        response = wechat_instance.response_text(
            content = (
                '感谢您的关注！\n回复【功能】查看支持的功能'
            )
        )
        if isinstance(message, TextMessage):
            # 当前会话内容
            content = message.content.strip()
            if content == u'功能':
                reply_text = (
                        '目前支持的功能：\n1.回复"温度"，查询室温\n'
                        '2.回复"状态"，查看当前屋内状态\n'
                        '3.回复"开灯"或"关灯"或"光控"，控制家中灯的亮灭\n'
                        '4.回复"打开监控"，当视频监控出现异常，自动报警；回复"关闭监控"，关闭报警功能\n'
                )
                response = wechat_instance.response_text(content=reply_text)
            elif content == u'温度':
                fp_tmp.seek(-4, 2)
                reply_text = "当前室温为" + fp_tmp.read(4) + "°C"
                response = wechat_instance.response_text(content=reply_text)
            elif content == u'状态':
                #response = wechat_instance.response_text(content="debug....")
                fp = open('galileo.jpg','rb')	
                upload_info = wechat_instance.upload_media("image", fp)
                image_id = upload_info['media_id']
                response = wechat_instance.response_image(image_id)
            elif content == u'开灯':
                light_flag = 1
                response = wechat_instance.response_text(content='灯已开')
            elif content == u'关灯':
                light_flag = 0
                response = wechat_instance.response_text(content='灯已关')
            elif content == u'光控':
                light_flag = 2
                response = wechat_instance.response_text(content='灯已调为光控模式,室内较暗时自动打开')
            elif content == u'打开监控':
                detect_flag = 1
                response = wechat_instance.response_text(content='视频监控已经打开，若发现异常将自动报警')
            elif content == u'关闭监控':
                detect_flag = 0
                response = wechat_instance.response_text(content='视频监控已经关闭')
                
        return HttpResponse(response, content_type="application/xml")

def checkSignature(request):
    signature=request.GET.get('signature',None)
    timestamp=request.GET.get('timestamp',None)
    nonce=request.GET.get('nonce',None)
    echostr=request.GET.get('echostr',None)
    #这里的token我放在setting，可以根据自己需求修改
    token="jcgalileo2"

    tmplist=[token,timestamp,nonce]
    tmplist.sort()
    tmpstr="%s%s%s"%tuple(tmplist)
    tmpstr=hashlib.sha1(tmpstr).hexdigest()
    if tmpstr==signature:
        return echostr
    else:
        return None
