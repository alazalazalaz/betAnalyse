
import requests
import time
import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import sys
sys.path.append("../")
import db.db as db
import numpy as np
import scipy
#Matplotlib是Python中最常用的可视化工具之一，可以非常方便地创建海量类型地2D图表和一些基本的3D图表。
import matplotlib.pyplot as plt



def getData():
	global date
	sql = "SELECT * FROM {tableName} WHERE match_time>={date} and match_time<{endDate} order by id desc".format(tableName = global_table_name, date = date, endDate = endDate)
	data = db.find(sql)
	return data

def drawImg(data):
	x = []
	y = []

	if data:
		for i  in range(0, len(data)):
			y.append(data[i]['re_334'])
			x.append(i)

	plt.figure()

	#绘制图案(第三个参数可由颜色、线条样式、标记样式组合)
	plt.plot(x, y, 'r--d', label='red line')
	plt.show()

def cal(data):
	result = {
		'red':{},
		'black':{}
	}
	lastStatus = '1';#上一轮的状态
	i = 1;#连续的次数
	overItem = 0#是否结算本轮
	lastI = 0
	for i in range(0, len(data)):
		status = data[i]
		if status == lastStatus:
			i += 1
			overItem = 0
		else:
			if status == '1':
				lastStatus = '-1'
			lastI = i
			i = 1
			overItem = 1

		if overItem == 1:
			pass

		


	print(result)

def main():
	data = getData()
	drawImg(data)
	# data = ['1', '1', '1']
	# cal(data)


db = db.Db('ds')
global date
date = '20180425'
global endDate
endDate = '20180500'
global_table_name = 'ds_history_05'
main()


