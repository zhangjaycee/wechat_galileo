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


WECHAT_TOKEN = 'jcgalileo'
AppID = ''
AppSecret = ''

fp_tmp = open('log_tmp.txt','wa')
fp_tmp_tail = open('log_tmp_tail.txt','wr')

# 实例化 WechatBasic
wechat_instance = WechatBasic(
    token=WECHAT_TOKEN
    #appid=AppID,
    #appsecret=AppSecret
)

@csrf_exempt
def index(request):
    if request.method=='GET':
        response=HttpResponse(checkSignature(request))
        return response
    else:
        xmlstr = smart_str(request.body)
        xml = etree.fromstring(xmlstr)
        temprature = xml.find('tmptature')
        if temprature:
            fp_tmp.write(temprature.text)
            os.system("tail -1 log_tmp.txt > log_tmp_tail.txt")

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
            if content == '功能':
                reply_text = (
                        '目前支持的功能：\n1...'
                        '2...\n'
                )
            if content == '温度':
                reply_text = fp_tmp_tail.realine()
                                                
            response = wechat_instance.response_text(content=reply_text)
 
        return HttpResponse(response, content_type="application/xml")

def checkSignature(request):
    signature=request.GET.get('signature',None)
    timestamp=request.GET.get('timestamp',None)
    nonce=request.GET.get('nonce',None)
    echostr=request.GET.get('echostr',None)
    #这里的token我放在setting，可以根据自己需求修改
    token="jcgalileo"

    tmplist=[token,timestamp,nonce]
    tmplist.sort()
    tmpstr="%s%s%s"%tuple(tmplist)
    tmpstr=hashlib.sha1(tmpstr).hexdigest()
    if tmpstr==signature:
        return echostr
    else:
        return None
