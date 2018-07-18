import sys
sys.path.append("../..")
import db.db as db


db = db.Db()
session = '17_18'
matchDataSession = 'nba_match_data_' + session
defaultAloRank = 1400 #初始时，每个球队的默认埃罗积分
defaultAloLimitK = 64 #输赢比赛最大的比分变化

def getData():
	'''获取一场已经比赛完了，但还没有计算埃罗积分的比赛'''
	sql = "SELECT * FROM {session} WHERE PTS>0 and alo_rank=0 limit 2".format(session = matchDataSession)
	data = db.find(sql)
	if len(data) <= 0:
		print("没有比赛啦")
		exit()

	twoTeam = {}
	for i in range(0, 2):
		if(data[i]['is_host'] == 1):
			twoTeam['host'] = data[i]
		else:
			twoTeam['guest'] = data[i]
	if(twoTeam['host']['match_id'] != twoTeam['guest']['match_id']):
		print("数据错误，这俩队不是一场比赛的", twoTeam)

	return twoTeam


def getInitAloRank(twoTeam):
	initAloRank = {'host':defaultAloRank, 'guest':defaultAloRank}
	sql = "SELECT alo_rank FROM {session} WHERE team_id={team} AND PTS>0 AND alo_rank>0 ORDER BY ID DESC LIMIT 1".\
	format(session = matchDataSession, team = twoTeam['host']['team_id'])

	data = db.find(sql)

	if len(data) > 0:
		initAloRank['host'] = data[0]['alo_rank']

	sql = "SELECT alo_rank FROM {session} WHERE team_id={team} AND PTS>0 AND alo_rank>0 ORDER BY ID DESC LIMIT 1".\
		format(session = matchDataSession, team = twoTeam['guest']['team_id'])

	data = db.find(sql)

	if len(data) > 0:
		initAloRank['guest'] = data[0]['alo_rank']

	return initAloRank


def calAloWinPercentage(twoTeam, beforeAloRank):
	calResult = {'host':{'alo_win_percentage':0, 'alo_rank':0}, 'guest':{'alo_win_percentage':0, 'alo_rank':0}}
	hostBeforeRank = beforeAloRank['host']
	guestBeforeRank= beforeAloRank['guest']

	hostWinPer = round(1 / (1 + 10 ** ((guestBeforeRank - hostBeforeRank)/400)), 4)
	guestWinPer = round(1 - hostWinPer, 4)
	calResult['host']['alo_win_percentage'] = 100 * hostWinPer
	calResult['guest']['alo_win_percentage'] = 100 * guestWinPer
	
	if twoTeam['host']['PTS'] > twoTeam['guest']['PTS']:
		hostWinAloChange = int(round(defaultAloLimitK * (1 - hostWinPer)))
	else:
		hostWinAloChange = int(round(defaultAloLimitK * (0 - hostWinPer)))

	calResult['host']['alo_rank'] = hostBeforeRank + hostWinAloChange
	calResult['guest']['alo_rank'] = guestBeforeRank - hostWinAloChange

	return calResult

def writeDb(twoTeam, beforeAloRank, calResult):
	updateData = calResult
	updateData['host']['alo_rank_before'] = beforeAloRank['host']
	updateData['guest']['alo_rank_before'] = beforeAloRank['guest']

	sqlHost = "UPDATE {session} SET alo_rank_before={before},alo_rank={rank},alo_win_percentage={per} WHERE id={id} LIMIT 1".\
	format(session = matchDataSession, before = updateData['host']['alo_rank_before'], rank = updateData['host']['alo_rank'], \
	per = updateData['host']['alo_win_percentage'], id = twoTeam['host']['id'])

	sqlGuest = "UPDATE {session} SET alo_rank_before={before},alo_rank={rank},alo_win_percentage={per} WHERE id={id} LIMIT 1".\
	format(session = matchDataSession, before = updateData['guest']['alo_rank_before'], rank = updateData['guest']['alo_rank'], \
	per = updateData['guest']['alo_win_percentage'], id = twoTeam['guest']['id'])

	db.update(sqlHost)
	db.update(sqlGuest)

	

def doMain(twoTeam):
	#获取两支队伍之前的积分情况
	beforeAloRank = getInitAloRank(twoTeam);

	#计算两支队的胜率和最终积分
	calResult = calAloWinPercentage(twoTeam, beforeAloRank);
	
	#入库
	writeDb(twoTeam, beforeAloRank, calResult)

	#log
	print("matchID:{matchID}   更新主队 {teamName} {before}=>{now}".format(matchID = twoTeam['host']['match_id'],\
		teamName = twoTeam['host']['team_name'].ljust(12),\
		before = beforeAloRank['host'], now = calResult['host']['alo_rank'] ))
	print("matchID:{matchID}   更新客队 {teamName} {before}=>{now}".format(matchID = twoTeam['guest']['match_id'],\
		teamName = twoTeam['guest']['team_name'].ljust(12),\
		before = beforeAloRank['guest'], now = calResult['guest']['alo_rank'] ))

def clearData():
	sql = "UPDATE {session} SET alo_rank_before=0,alo_rank=0,alo_win_percentage=0.00".format(session = matchDataSession);
	db.update(sql)




def main():
	'''使用nba_match_data_xx表里面的数据，计算出每个球队的ALO积分情况'''
	#清空该赛季的数据再来计算
	# clearData()

	#计算并入库
	for i in range(0, 1300):
		#获取要计算埃罗积分的两支队伍
		twoTeam = getData();
		doMain(twoTeam)


main()


# -- 最大rank
# select data.team_id,max(data.alo_rank) as rank,team.name,team.area_name
# from nba_match_data_13_14 as data 
# left join nba_team as team on data.team_id=team.tid 
# group by data.team_id order by rank desc;

# -- 最终rank;

# select a.*,team.area_name from (select team_id,match_id,team_name,alo_rank_before,alo_rank,alo_win_percentage,FROM_UNIXTIME(match_time) from nba_match_data_13_14 
# where team_id in (select tid from nba_team) order by id desc limit 30) as a
# left join nba_team as team on a.team_id=team.tid
#  order by a.alo_rank desc;


