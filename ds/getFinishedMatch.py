
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

def getData(searchTime, page):
	
	url = 'https://api.dszuqiu.com/v6/diary'

	#拉取最近的已完成的数据
	# data = {'last':1, 'page':page, 'per_page':20, 'request_time':time.time(), 'token':'212099-e255e9d6cf8d9ae99b029aaae16b5e6c'}
	#拉取昨天的数据第一页数据为00:00开始的数据，最后一页为晚上的数据
	data = {'day':searchTime, 'only_need':2, 'page':page, 'per_page':20, 'request_time':time.time(), 'token':'212099-e255e9d6cf8d9ae99b029aaae16b5e6c'}
	getResult = requests.post(url, params = data)

	return getResult.text

def doData(resultString, matchTime):
	global global_one_day_data
	resultJson = json.loads(resultString)
	matchList = resultJson['races']
	if matchList:
		for i in range(0, len(matchList)):
			events = matchList[i]['events_graph']['events']
			matchAt = matchList[i]['race_time']
			matchId = matchList[i]['id']
			leagueName = matchList[i]['league']['name'].replace("'", " ")
			hostName = matchList[i]['host']['name'].replace("'", " ")
			guestName = matchList[i]['guest']['name'].replace("'", " ")

			if filterLeague(leagueName) == False:
				continue

			if events:
				global_one_day_data.append([matchId, leagueName, hostName, guestName, json.dumps(events), matchTime, matchAt])
				
		return True
	else:
		return False


def main(historyDay):
	global global_one_day_data
	for i in range(0, historyDay):
		global_one_day_data = []
		currentTime = int(time.time()) - 86400 * i
		searchTime = time.strftime("%Y%m%d", time.localtime(currentTime))
		do(searchTime)
		batchInsert()

	

def do(searchTime):
	for i in range(1, 50):
		page = i
		data = doData(getData(searchTime, page), searchTime)

def batchInsert():
	global global_one_day_data
	keys = ['match_id', 'league_name', 'host_name', 'guest_name', 'events', 'match_time', 'match_at'];
	try:
		db.insertBatch(global_table_name, keys, global_one_day_data)
	except Exception as e:
		for j in range(0, len(global_one_day_data)):
			try:
				db.insertBatch(global_table_name, keys, [global_one_day_data[j]])
			except Exception as e:
				# print(global_one_day_data[j]['5'])
				print('error')
				# exit()

def filterLeague(leagueName):
	if (leagueName[:3] == '俄罗斯') or (leagueName[:3] == '乌克兰') or (leagueName[:2] == '俄丙'):
		return False
	else:
		return True


global_table_name = 'ds_finished_match'
global global_one_day_data

db = db.Db('ds')
historyDay = 1
main(historyDay)

print('ok')


