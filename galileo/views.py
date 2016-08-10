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
import time
from socket import *
##mysql
#import plotly.plotly as py
#import plotly.offline as pyofl 
#import plotly.graph_objs as go
#import plotly.tools as tls
#tls.set_credentials_file(username='zhangjaycee', api_key='3bpq5egpcf')
#import numpy as np
import pandas as pd
import MySQLdb
import re
conn = MySQLdb.connect(host="localhost", user="root", passwd="123", db="health_db")
cursor = conn.cursor()
##

'''
WECHAT_TOKEN = 'jcgalileo'
AppID = 'wx4b7943f082770e22'
AppSecret = '60186ab20d8e44bf2e7c496a9e7a34a1'
'''
WECHAT_TOKEN = 'jcgalileo2'
AppID = 'wx5a13781f1ae1b5be'
AppSecret = 'd4624c36b6795d1d99dcf0547af5443d'

MY_OPENID = 'o2cILxORC3vAZHOMrCgcfeixBT2w' #zjc
#MY_OPENID = 'o2cILxJ41HJ9bGG5NSWKXo1HjLtk' #ksx

# 实例化 WechatBasic
wechat_instance = WechatBasic(
    token=WECHAT_TOKEN,
    appid=AppID,
    appsecret=AppSecret
)

post_time = '0000-00-00 00:00'
start_seat_time = 0
end_seat_time = 0
#seat_status_flag  = 0
seat_time = 0
arr = []
seek_times = []
#arr[0:] = "%d" % seat_status_flag
@csrf_exempt
def index(request):
    global post_time
    #global start_seat_time
    #global end_seat_time
    #global seat_status_flag
    #global seat_time
    global cursor
    global conn
    global arr

    if request.method=='GET':
        response=HttpResponse(checkSignature(request))
        return response
    else:
        xmlstr = smart_str(request.body)
        xml = etree.fromstring(xmlstr)
        #temprature = xml.find('temprature')
        #light = xml.find('light')
        #dangerous = xml.find('dangerous')
        
        #heart_rate = xml.find('heart_rate') #心跳
        #breath = xml.find('breath') #呼吸率
        #hrv = xml.find('hrv')
        #outblood = xml.find('outblood')
        #seat_status = xml.find('status')

        sum_data = xml.find('sum')
        seek_data = xml.find('seek')
        
        if seek_data != None:
            seek_times = re.split('/|,| |:', seek_data.text)
            seek_time1 = "%s-%s-%s %s:%s" % (seek_times[2], seek_times[0], seek_times[1], seek_times[3], seek_times[4])
            seek_time2 = "%s-%s-%s %s:%s" % (seek_times[7], seek_times[5], seek_times[6], seek_times[8], seek_times[9])
            exe_cmd = "SELECT month, day, hour, minutes, heart_rate, id from timeline where createtime between '%s' and '%s'" %(seek_time1, seek_time2)
            sock = socket(AF_INET, SOCK_STREAM);
            sock.connect(('localhost', 6767));
            sock.send(exe_cmd);
            szBuf = sock.recv(1024);
            print("recv " + szBuf);
            sock.close();
            print("end of connect");
            '''
            cursor.execute(exe_cmd)
            rows = cursor.fetchall()
            if rows == None:
                return HttpResponse("no data")
            df = pd.DataFrame([[j for j in i] for i in rows])
            df.rename(columns={0:'month', 1:'day', 2:'hour', 3:'minutes', 4:'heart_rate', 5:'id'}, inplace=True)
            time_id = []
            for i in range(len(df['id'])):
                if rows[i][3] >= 10: 
                    time_id.append("%d-%d %d:%d" % (rows[i][0], rows[i][1], rows[i][2], rows[i][3]))
                else:
                    time_id.append("%d-%d %d:0%d" % (rows[i][0], rows[i][1], rows[i][2], rows[i][3]))
            axisx = [i for i in range(len(df['id']))]
            trace1 = go.Scatter(
                x=axisx,
                y=df['heart_rate'],
                text = time_id
                #mode='maekers'
            )
            layout = go.Layout(
                xaxis=go.XAxis(title=' '),
                yaxis=go.YAxis(title='次/分钟')
            )
            data = go.Data([trace1])
            fig = go.Figure(data=data, layout=layout)
            plot_url = pyofl.plot(fig, filename='/root/sites/blog/graph0')
            '''
            #reply_text = u"查询完成，网址为：<a href=\"http://blog.jcix.top/graph0.html\">点击进入</a>"
            #wechat_instance.send_text_message(MY_OPENID, reply_text)
            return HttpResponse("seek done")
        if sum_data != None:
            post_time = time.strftime("%Y-%m-%d %H:%M",time.localtime(time.time()))
            cursor.execute('SELECT year, month, day, hour, minutes from timeline order by id desc limit 1')
            rows = cursor.fetchall()
            arr[0:] = "1"
            arr[1:] = re.split('-| |:', post_time)
            arr[6:] = re.split(',| ', sum_data.text)
            if rows[0][0] == int(arr[1]) and rows[0][1] == int(arr[2]) and rows[0][2] == int(arr[3]) and rows[0][3] == int(arr[4]) and rows[0][4] == int(arr[5]):
                return HttpResponse("rejected!have committed this minute")
            execute_str = "insert into timeline(status, year, month, day, hour, minutes, heart_rate, breath_rate, blood, hrv) values('%s','%s','%s','%s', '%s','%s','%s','%s','%s','%s')" % tuple(arr)
            cursor.execute(execute_str)
            conn.commit()
            if float(arr[6]) < 60 :
                wechat_instance.send_text_message(MY_OPENID, u"心率过低！（" + arr[6] + u"次每分钟,数据更新时间" + post_time + ')')
            if float(arr[6]) > 100:
                wechat_instance.send_text_message(MY_OPENID, u"心率过高！（" + arr[6] + u"次每分钟,数据更新时间" + post_time + ')')
            return HttpResponse("mysql committed:"+execute_str)
        
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
                        '功能：\n1.回复"心率"，查询最近一分钟的心率\n'
                        '2.回复"状态"，查看座椅上是否有人以及近期心率走势图\n'
                        '3.回复“呼吸”，查询最近一分钟的呼吸率\n'
                        '4.回复“排血量”，查询最近一分钟的排血量\n'
                        '5.回复“HRV”，查询最近一分钟的心脏变异率\n'
                )
                response = wechat_instance.response_text(content=reply_text)
            elif content == u'心率':
                cursor.execute('SELECT heart_rate, year, month, day, hour, minutes from timeline order by id desc limit 1')
                rows = cursor.fetchall()  
                if rows[0][5] <10:
                    rows = (rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4], "0%d" % rows[0][5])
                else:
                    rows = (rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4], "%d" % rows[0][5])
                reply_text = "心率为%d次每分钟, 数据更新时间：%d-%d-%d %d:%s" % rows
                response = wechat_instance.response_text(content=reply_text)
            elif content == u'呼吸':
                cursor.execute('SELECT breath_rate, year, month, day, hour, minutes from timeline order by id desc limit 1')
                rows = cursor.fetchall()
                if rows[0][5] <10:
                    rows = (rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4], "0%d" % rows[0][5])
                else:
                    rows = (rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4], "%d" % rows[0][5])
                reply_text = "呼吸率为%d次每分钟, 数据更新时间：%d-%d-%d %d:%s" % rows
                response = wechat_instance.response_text(content=reply_text)
            elif content == u'排血量':
                cursor.execute('SELECT blood, year, month, day, hour, minutes from timeline order by id desc limit 1')
                rows = cursor.fetchall()
                if rows[0][5] <10:
                    rows = (rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4], "0%d" % rows[0][5])
                else:
                    rows = (rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4], "%d" % rows[0][5])
                reply_text = "排血量为为%d毫克每分钟, 数据更新时间：%d-%d-%d %d:%s" % rows
                response = wechat_instance.response_text(content=reply_text)
            elif content == u'HRV' or content == u'hrv' or content == u'Hrv':
                cursor.execute('SELECT hrv, year, month, day, hour, minutes from timeline order by id desc limit 1')
                rows = cursor.fetchall()
                if rows[0][5] <10:
                    rows = (rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4], "0%d" % rows[0][5])
                else:
                    rows = (rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4], "%d" % rows[0][5])
                reply_text = "心脏变异性为%d毫秒, 数据更新时间：%d-%d-%d %d:%s" % rows
                response = wechat_instance.response_text(content=reply_text)
            elif content == u'状态':
                seat_status_flag = 0
                post_time1 = time.strftime("%Y-%m-%d %H:%M",time.localtime(time.time()))
                time_arr = re.split('-| |:', time.strftime("%Y-%m-%d %H:%M",time.localtime(time.time())))
                for i in range(5):
                    time_arr[i] = int(time_arr[i])
                cursor.execute('SELECT year, month, day, hour, minutes from timeline order by id desc limit 1')
                rows = cursor.fetchall()
                if time_arr[0] == rows[0][0] and time_arr[1] == rows[0][1] and time_arr[2] == rows[0][2]:
                    if time_arr[3] == rows[0][3] and time_arr[4] - rows[0][4] <= 5:
                        seat_status_flag = 1
                    if time_arr[3] - rows[0][3] == 1 and time_arr[4] + 60 - rows[0][4] <=5:
                        seat_status_flag = 1
                sock = socket(AF_INET, SOCK_STREAM);
                sock.connect(('localhost', 6767));
                sock.send("status");
                szBuf = sock.recv(1024);
                print("recv " + szBuf);
                sock.close();
                print("end of connect");
                '''
                exe_cmd = 'SELECT month, day, hour, minutes, heart_rate,id from timeline where id > (select MAX(id) from timeline) - 20'
                cursor.execute(exe_cmd)
                rows = cursor.fetchall()
                df = pd.DataFrame([[j for j in i] for i in rows])
                df.rename(columns={0:'month', 1:'day', 2:'hour', 3:'minutes', 4:'heart_rate', 5:'id'}, inplace=True)
                time_id = []
                for i in range(len(df['id'])):
                    if rows[i][3] >= 10: 
                        time_id.append("%d-%d %d:%d" % (rows[i][0], rows[i][1], rows[i][2], rows[i][3]))
                    else:
                        time_id.append("%d-%d %d:0%d" % (rows[i][0], rows[i][1], rows[i][2], rows[i][3]))
                axisx = [i for i in range(len(df['id']))]
                trace1 = go.Scatter(
                    x=axisx,
                    y=df['heart_rate'],
                    text = time_id
                    #mode='maekers'
                )
                layout = go.Layout(
                    xaxis=go.XAxis(title=' '),
                    yaxis=go.YAxis(title='次/分钟')
                )
                data = go.Data([trace1])
                fig = go.Figure(data=data, layout=layout)
                plot_url = pyofl.plot(fig, filename='/root/sites/blog/graph1')
                '''
                cursor.execute('SELECT heart_rate, breath_rate, year, month, day, hour, minutes from timeline order by id desc limit 1')
                rows = cursor.fetchall()
                if rows[0][6] <10:
                    rows = (rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4], rows[0][5], "0%d" % rows[0][6])
                else:
                    rows = (rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4], rows[0][5], "%d" % rows[0][6])
                if seat_status_flag == 1:
                    reply_text = u"当前椅子上【有人】\n心率为%s次每分钟\n呼吸率%s次每分钟\n数据更新时间:\n%d-%d-%d %d:%s\n" % rows
                    reply_text += u"\n<a href=\"http://blog.jcix.top/graph1.html\">点击查看近期心率走势图</a>"
                else:
                    reply_text = u"当前椅子上【无人】\n"
                    reply_text += u"\n<a href=\"http://blog.jcix.top/graph1.html\">点击查看近期心率走势图</a>"
                response = wechat_instance.response_text(content=reply_text)
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
