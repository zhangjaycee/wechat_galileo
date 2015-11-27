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

fp_tmp = open('log_tmp.txt','a+')

# 实例化 WechatBasic
wechat_instance = WechatBasic(
    token=WECHAT_TOKEN,
    appid=AppID,
    appsecret=AppSecret
)

@csrf_exempt
def index(request):
    if request.method=='GET':
        response=HttpResponse(checkSignature(request))
        return response
    else:
        xmlstr = smart_str(request.body)
        xml = etree.fromstring(xmlstr)
        temprature = xml.find('temprature')
        if temprature != None:
            fp_tmp.seek(0,2)
            fp_tmp.write(temprature.text)
            return HttpResponse("0")
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
                        '目前支持的功能：\n1.回复“温度”，查询113室温\n'
                        '2.回复“拍照”，偷窥jc的生活状态\n'
                )
                response = wechat_instance.response_text(content=reply_text)
            if content == u'温度':
                fp_tmp.seek(-4, 2)
                reply_text = fp_tmp.read(4)
                response = wechat_instance.response_text(content=reply_text)
            if content == u'拍照':
                #response = wechat_instance.response_text(content="debug....")
		fp = open('galileo.jpg','rb')	
		upload_info = wechat_instance.upload_media("image", fp)
		image_id = upload_info['media_id']
                response = wechat_instance.response_image(image_id)
 
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
