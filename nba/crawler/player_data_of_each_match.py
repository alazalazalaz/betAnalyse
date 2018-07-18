import sys
sys.path.append("../../")
import db.db as db
import requests
import time

session = '17_18'
matchListTable 	= 'nba_match_list_' + session
matchDataTable	= 'nba_match_data_' + session
playerDataTable	= 'nba_player_data_' + session

dbObj = db.Db('nba')

def getMatchList():
	'''获取比赛列表信息'''
	todayTime = time.time()
	sql = "SELECT * FROM {table} WHERE match_time<{time} AND match_id not in (select match_id from {match_data_table}) and match_state!=-5".format(table=matchListTable, time = int(todayTime), match_data_table = matchDataTable)
	matchList = dbObj.find(sql)
	return matchList


def curlMatchData(matchBaseInfo):
	'''根据比赛ID获取比赛数据'''
	matchId = matchBaseInfo['match_id']
	matchTime = matchBaseInfo['match_time']
	e = str(matchId)[1:3]
	first = str(matchId)[0:1]

	url = "http://nba.win007.com/jsData/tech/{first}/{e}/{match_id}.js?flesh=0.004348608612015248".format(match_id = matchId, e=e, first=first)
	
	curlData = requests.get(url)

	teamIds = ['', matchBaseInfo['host_id'], matchBaseInfo['guest_id']]
	teamNames = ['', matchBaseInfo['host_name'], matchBaseInfo['guest_name']]

	result = {'insertPlayer':[], 'insertMatchInfo': []}
	if len(curlData.text)<=0:
		return result

	for i in range(1, 3):
		teamData = curlData.text.split('$')[i].split('!')

		isWin = 0

		if i == 1 and matchBaseInfo['host_score'] > matchBaseInfo['guest_score']:
			isWin = 1
		elif i == 2 and matchBaseInfo['host_score'] < matchBaseInfo['guest_score']:
			isWin = 1

		isHost  = 1 if i == 1 else 0
		teamInfo = [matchId, matchTime, isHost, isWin, teamIds[i], teamNames[i]]

		for player in teamData:

			item = player.split('^')
			itemLen = len(item)
			if itemLen == 6:
				'''球队数据'''
				teamInfo.append(item[1])		#球队投篮命中率%	FG%
				teamInfo.append(item[2])	#球队三分投篮命中率	3P%
				teamInfo.append(item[3])		#罚球命中率	FT%
			
			elif itemLen == 16:
				'''球队数据'''
				teamInfo.append(item[1])	#投篮进球次数  FG
				teamInfo.append(item[2])	#投篮总次数(含2分3分)	 FGA
				teamInfo.append(item[3])	#3分进球次数  3P
				teamInfo.append(item[4])	#3分投篮次数  3PA
				teamInfo.append(item[5])	#罚球命中		FT
				teamInfo.append(item[6])	#罚球总次数	FTA
				teamInfo.append(item[7])	#进攻篮板		ORB
				teamInfo.append(item[8])	#防守篮板		DRB
				teamInfo.append(item[9])	#总篮板		TRB
				teamInfo.append(item[10])	#总助攻		AST
				teamInfo.append(item[11])   #犯规		PF
				teamInfo.append(item[12])	#抢断		STL
				teamInfo.append(item[13])	#失误		TOV
				teamInfo.append(item[14])	#盖帽		BLK
				teamInfo.append(item[15])	#得分		PTS

			else:
				'''个人数据'''
				playerId 					= item[0]	#ID
				playerName 					= item[1]	#姓名		 NAME
				playerMinute 				= item[6]	#上场分钟		 MIN
				playerFieldGoal				= item[7]	#投篮进球次数  FG
				playerFieldGoalAttempts 	= item[8]	#投篮总次数(含2分3分)	 FGA
				player3FieldGoal 			= item[9]	#3分进球次数  3P
				player3FieldGoalAttempts 	= item[10]	#3分投篮次数  3PA
				playerFreeThrow 			= item[11]	#罚球命中		FT
				playerFreeThrowAttempts		= item[12]	#罚球总次数	FTA
				playerOffensiveRebound 		= item[13]	#进攻篮板		ORB
				playerDefenseRebound 		= item[14]	#防守篮板		DRB
				playerTotalRebound 			= item[15]	#总篮板		TRB
				playerAssist				= item[16]	#总助攻		AST
				playerPersonalFouls			= item[17]  #犯规		PF
				playerSteal					= item[18]	#抢断		STL
				playerTurnover				= item[19]	#失误		TOV
				playerBlocks				= item[20]	#盖帽		BLK
				playerScoring				= item[21]	#得分		PTS

				tempPersonal = [matchId, teamIds[i], playerId, playerName, playerMinute, playerFieldGoal, playerFieldGoalAttempts,player3FieldGoal, player3FieldGoalAttempts,
				playerFreeThrow, playerFreeThrowAttempts, playerOffensiveRebound, playerDefenseRebound, playerTotalRebound, playerAssist,
				playerPersonalFouls, playerSteal, playerTurnover, playerBlocks, playerScoring]

				result['insertPlayer'].append(tempPersonal)
		
		result['insertMatchInfo'].append(teamInfo)
	return result



#run

def main():
	matchList = getMatchList()

	keysPlayer = ['match_id', 'team_id', 'player_id', 'name', 'MIN', 'FG', 'FGA', '3P', '3PA', 'FT', 
	'FTA', 'ORB', 'DRB', 'TRB', 'AST', 'PF', 'STL', 'TOV', 'BLK', 'PTS']

	keysTeam = ['match_id', 'match_time', 'is_host', 'is_win', 'team_id', 'team_name', 'FG', 'FGA', '3P', '3PA', 'FT', 
	'FTA', 'ORB', 'DRB', 'TRB', 'AST', 'PF', 'STL', 'TOV', 'BLK', 'PTS', 'FG%', '3P%', 'FT%']

	for x in range(0, len(matchList)):
		insertData = curlMatchData(matchList[x])
		print(x, matchList[x]['id'], matchList[x]['match_id'])
		re1 = False
		re2 = False
		if len(insertData['insertPlayer'])>0:
			re1 = dbObj.insertBatch(playerDataTable, keysPlayer, insertData['insertPlayer'])
		if len(insertData['insertMatchInfo'])>0:
			re2 = dbObj.insertBatch(matchDataTable, keysTeam, insertData['insertMatchInfo'])
		print(re1, re2)

main()

# @todo 球员数据表，插入的列需要多增加几个，比如时间，比赛ID等，
# @todo 插入球队比赛的结果到match_list表
# @todo 把15-16赛季的数据全部抓完就可以开始对比
# @todo 抓取16-17赛季的来预测



