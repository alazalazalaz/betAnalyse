
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

	data = {'day':searchTime, 'only_need':2, 'page':page, 'per_page':20, 'request_time':time.time(), 'token':'212099-e255e9d6cf8d9ae99b029aaae16b5e6c'}
	getResult = requests.post(url, params = data)

	return getResult.text

def doData(resultString, matchTime):
	resultJson = json.loads(resultString)
	matchList = resultJson['races']
	if matchList:
		insertValue = []
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
				goal_30 = 0
				goal_45 = 0
				goal_75 = 0
				goal_90 = 0
				re_334 = 0
				re_757 = 0
				for k in range(0, len(events)):
					status = int(events[k]['status'])
					t = events[k]['t']
					if (t == 'gg') or (t == 'hg'):
						if status < 30:
							goal_30 += 1
						if status <= 45:
							goal_45 += 1
						if status < 75:
							goal_75 += 1
						if status <= 90:
							goal_90 += 1

					if (goal_30 == 3 and goal_45 > 3) or (goal_30 > 3):
						re_334 = 1
					elif (goal_30 ==3 and goal_45 <= 3):
						re_334 = -1

					if (goal_75 == 6 and goal_90 > 6) or (goal_75 > 6):
						re_757 = 1
					elif (goal_75 ==6 and goal_90 <= 6):
						re_757 = -1

				insertValue.append([matchId, leagueName, hostName, guestName, goal_30, goal_45, goal_75, goal_90, re_334, re_757, matchTime, matchAt])
		
		if insertValue:
			keys = ['match_id', 'league_name', 'host_name', 'guest_name', 'goal_30', 'goal_45', 'goal_75', 'goal_90', 're_334', 're_757', 'match_time', 'match_at'];
			try:
				db.insertBatch('ds_history', keys, insertValue)
			except Exception as e:
				print('over')
				exit()
			

		return True
	else:
		return False


def main(historyDay):
	for i in range(0, historyDay):
		currentTime = int(time.time()) - 86400 * i
		searchTime = time.strftime("%Y%m%d", time.localtime(currentTime))

		do(searchTime)

	

def do(searchTime):
	for i in range(1, 50):
		page = i
		data = doData(getData(searchTime, page), searchTime)
		if data == False:
			break


def filterLeague(leagueName):
	if (leagueName[:3] == '俄罗斯') or (leagueName[:3] == '乌克兰'):
		return False
	else:
		return True



db = db.Db('ds')
historyDay = 3
main(historyDay)


print('ok')


