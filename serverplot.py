#!/usr/bin/env python
#coding:utf-8

from socket import *
import plotly.offline as pyofl
import plotly.graph_objs as go
import plotly.tools as tls
import pandas as pd
#import numpy as np  ##
import MySQLdb

conn = MySQLdb.connect(host="localhost", user="root", passwd="123", db="health_db")
cursor = conn.cursor()
host ='127.0.0.1'
port = 6767
addr = (host, port)
ss = socket(AF_INET,SOCK_STREAM) 
ss.bind(addr)    
ss.listen(5)  
while True:
    print 'waiting for a client connection...'
    SockClientConnect,ClientAddr = ss.accept()
    print'...connection from:', ClientAddr
    data = SockClientConnect.recv(1024)     
    print data
    if data == "close":
        break
    elif data == "status":
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
        pyofl.plot(fig, filename='/root/sites/blog/graph1.html')
        SockClientConnect.send('socketok')
        SockClientConnect.close()
    else:
        cursor.execute(data)
        rows = cursor.fetchall()
        if rows == None:
            SockClientConnect.send('socket no data')
            SockClientConnect.close()
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
        SockClientConnect.send('socketok')
        SockClientConnect.close()
    print "conn closing."
ss.close()
