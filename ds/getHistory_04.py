
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


def doData(matchList):
	if matchList:
		insertValue = []
		for i in range(0, len(matchList)):
			events = json.loads(matchList[i]['events'])
			matchAt = matchList[i]['match_at']
			matchTime = matchList[i]['match_time']
			matchId = matchList[i]['match_id']
			leagueName = matchList[i]['league_name'].replace("'", " ")
			hostName = matchList[i]['host_name'].replace("'", " ")
			guestName = matchList[i]['guest_name'].replace("'", " ")

			if events:
				goal_30 = 0
				goal_45 = 0
				goal_75 = 0
				goal_90 = 0
				re_334 = 0
				re_757 = 0
				goal_20 = 0;
				for k in range(0, len(events)):
					status = int(events[k]['status'])
					t = events[k]['t']
					if (status < 20) and ((t == 'gg') or (t == 'hg')):
						goal_20 += 1
					if (status < 30) and ((t == 'gg') or (t == 'hg')):
						goal_30 += 1
					if status <= 45:
						if (status < 30) and ((t == 'gg') or (t == 'hg')):
							goal_45 += 1
						elif (status >= 30) and ((t == 'gg') or (t == 'hg') or (t == 'gp') or (t == 'hp')):
							goal_45 += 1

				if (goal_30 == 3 and goal_45 > 3):
					re_334 = 1
				elif (goal_30 ==3 and goal_45 <= 3):
					re_334 = -1

				# if (goal_75 == 6 and goal_90 > 6):
				# 	re_757 = 1
				# elif (goal_75 ==6 and goal_90 <= 6):
				# 	re_757 = -1

				if re_334 != 0 and goal_20 < 3:
					insertValue.append([matchId, leagueName, hostName, guestName, goal_30, goal_45, goal_75, goal_90, re_334, re_757, matchTime, matchAt])
		
		if insertValue:
			keys = ['match_id', 'league_name', 'host_name', 'guest_name', 'goal_30', 'goal_45', 'goal_75', 'goal_90', 're_334', 're_757', 'match_time', 'match_at'];
			try:
				db.insertBatch(global_table_name, keys, insertValue)
			except Exception as e:
				for j in range(0, len(insertValue)):
					try:
						db.insertBatch(global_table_name, keys, [insertValue[j]])
					except Exception as e:
						print('over')
						exit()
				
			

		return True
	else:
		return False


def getData(page, limit = 1000):
	m = (page - 1) * limit
	sql = "SELECT * from ds_finished_match limit " + str(m) + "," + str(limit)
	data = db.find(sql)
	return data

def main():
	for i in range(1,80):
		page = i
		data = getData(page)
		doData(data)

#01算法，33分钟(不含)前等于3个，半场>3个，算红
# global_table_name = 'ds_history_01'

#02算法，33分钟(不含)前等于3个，半场>3个，并且20分钟前<3，算红
# global_table_name = 'ds_history_02'

#04算法，同02算法，时间从33=>30
global_table_name = 'ds_history_04'

db = db.Db('ds')
main()


print('ok')


