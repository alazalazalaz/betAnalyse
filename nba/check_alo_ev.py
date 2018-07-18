import sys
sys.path.append("..")
import db.db as db
import time
import matplotlib.pyplot as plt


db = db.Db()
session = '17_18'
matchDataSession = 'nba_match_data_' + session
matchListSession = 'nba_match_list_' + session


def getMatchList():
	sql = "SELECT * FROM {table}".format(table = matchListSession)
	data = db.find(sql)
	return data

def getTeamData(matchId):
	sql = "SELECT * FROM {table} where match_id={id} AND alo_win_percentage!=50".format(table = matchDataSession, id=matchId)
	data = db.find(sql)
	return data

def compareMatch(matchDataResult, match):
	hostData = {}
	guestData = {}
	if matchDataResult[0]['is_host'] == 1:
		hostData = matchDataResult[0]
		guestData = matchDataResult[1]
	else:
		hostData = matchDataResult[1]
		guestData = matchDataResult[0]

	pridictionWinTeam = {}
	pridictionOdd = ''
	if hostData['alo_win_percentage'] > 50:
		pridictionWinTeam = hostData
		pridictionOdd = match['host_odd']
	else:
		pridictionWinTeam = guestData
		pridictionOdd = match['guest_odd']

	if pridictionWinTeam['alo_rank'] > pridictionWinTeam['alo_rank_before']:
		return pridictionOdd

	return 0

def compareMatchOpposite(matchDataResult, match):
	hostData = {}
	guestData = {}
	if matchDataResult[0]['is_host'] == 1:
		hostData = matchDataResult[0]
		guestData = matchDataResult[1]
	else:
		hostData = matchDataResult[1]
		guestData = matchDataResult[0]

	pridictionWinTeam = {}
	pridictionOdd = ''
	if hostData['alo_win_percentage'] < 50:
		pridictionWinTeam = hostData
		pridictionOdd = match['host_odd']
	else:
		pridictionWinTeam = guestData
		pridictionOdd = match['guest_odd']

	if pridictionWinTeam['alo_rank'] > pridictionWinTeam['alo_rank_before']:
		return pridictionOdd

	return 0

def calTotalEv(opposite = ''):
	matchList = getMatchList()

	compareMatchNum = 0
	compareWinMatchNum = 0
	totalWinOdd = 0
	for i in range(0, len(matchList)):
		matchId = matchList[i]['match_id']
		matchData = getTeamData(matchId)
		if len(matchData) <= 0:
			continue

		if opposite == 'opposite':
			odd = compareMatchOpposite(matchData, matchList[i])	
		else:
			odd = compareMatch(matchData, matchList[i])
		compareMatchNum += 1
		if odd > 0:
			compareWinMatchNum += 1
			totalWinOdd += odd

		date = time.strftime("%Y-%m-%d", time.localtime(matchList[i]['match_time']))
		# print("{time} {host_name} {guest_name} result: {odd}".format(time = date, host_name = matchList[i]['host_name'], guest_name = matchList[i]['guest_name'], odd = odd))		
		
	print('总场数，胜场数， 胜率, 收入， 支出')
	print(compareMatchNum, compareWinMatchNum, round(compareWinMatchNum*100/compareMatchNum, 2) , totalWinOdd, compareMatchNum)
	print('总盈利')
	print((totalWinOdd - compareMatchNum))

def calMonthEv(dayOrMonth):
	matchList = getMatchList()

	compareMatchNum = 0
	compareWinMatchNum = 0
	totalWinOdd = 0
	result = {}
	for i in range(0, len(matchList)):
		matchId = matchList[i]['match_id']
		if dayOrMonth == 'month':
			matchTimeMonth = time.strftime("%Y-%m", time.localtime(matchList[i]['match_time']))	
		elif dayOrMonth == 'day':
			matchTimeMonth = time.strftime("%Y-%m-%d", time.localtime(matchList[i]['match_time']))
		elif dayOrMonth == 'match':
			matchTimeMonth = time.strftime("%Y-%m-%d", time.localtime(matchList[i]['match_time'])) + str(matchList[i]['match_id'])
		if matchTimeMonth not in result:
			result[matchTimeMonth] = {'total':0, 'win':0, 'odd':0}

		matchData = getTeamData(matchId)
		if len(matchData) <= 0:
			continue

		odd = compareMatch(matchData, matchList[i])

		result[matchTimeMonth]['total'] += 1
		compareMatchNum += 1
		if odd > 0:
			compareWinMatchNum += 1
			totalWinOdd += odd
			result[matchTimeMonth]['win'] += 1
			result[matchTimeMonth]['odd'] += odd

	x = []
	y = []
	for date,item in result.items():
		total = item['total']
		if total <= 0:
			continue
		win = item['win']
		odd = round(item['odd'], 2)
		rate = str(round(100*win/total, 2)) + '%'
		ev = round(odd - total, 4)
		print("日期：{0}, 场数：{1}, 胜场：{2}, 胜率：{3}, 收入：{4}, 支出：{5}, 总盈利：{6}".format(\
			date, 			total, 	win, 		rate, 	odd, 		total, 		ev))
		#画图
		x.append(date)
		y.append(ev)

	plt.plot(x, y, 'r-d', label='red line')
	plt.grid()
	plt.show()

def calMonthEvOpposite(dayOrMonth):
	matchList = getMatchList()

	compareMatchNum = 0
	compareWinMatchNum = 0
	totalWinOdd = 0
	result = {}
	for i in range(0, len(matchList)):
		matchId = matchList[i]['match_id']
		if dayOrMonth == 'month':
			matchTimeMonth = time.strftime("%Y-%m", time.localtime(matchList[i]['match_time']))	
		elif dayOrMonth == 'day':
			matchTimeMonth = time.strftime("%Y-%m-%d", time.localtime(matchList[i]['match_time']))
		if matchTimeMonth not in result:
			result[matchTimeMonth] = {'total':0, 'win':0, 'odd':0}

		matchData = getTeamData(matchId)
		if len(matchData) <= 0:
			continue

		odd = compareMatchOpposite(matchData, matchList[i])

		result[matchTimeMonth]['total'] += 1
		compareMatchNum += 1
		if odd > 0:
			compareWinMatchNum += 1
			totalWinOdd += odd
			result[matchTimeMonth]['win'] += 1
			result[matchTimeMonth]['odd'] += odd

	x = []
	y = []
	for date,item in result.items():
		total = item['total']
		if total <= 0:
			continue
		win = item['win']
		odd = round(item['odd'], 2)
		rate = str(round(100*win/total, 2)) + '%'
		ev = round(odd - total, 4)
		print("日期：{0}, 场数：{1}, 胜场：{2}, 胜率：{3}, 收入：{4}, 支出：{5}, 总盈利：{6}".format(\
			date, 			total, 	win, 		rate, 	odd, 		total, 		ev))
		#画图
		x.append(date)
		y.append(ev)

	plt.plot(x, y, 'r-d', label='red line')
	plt.grid()
	plt.show()

def main():
	#计算总盈利
	calTotalEv()

	#计算每个月盈利情况
	# calMonthEv('month')
	calMonthEv('day')
	# calMonthEv('match')

	#计算反买
	# calTotalEv('opposite')
	# calMonthEvOpposite('day')


main()


