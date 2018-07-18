import sys
import numpy as np
sys.path.append("../../")
import db.db as db
import matplotlib.pyplot as plt
import time
import algorithm.linearRegressionNormal as linearRegressionNormal

db = db.Db()

pridiction_session = '17_18'

def lineAlgorithm(X, Y):
	'''线性回归-常规方程法:θ = (X转置矩阵 * X)的逆矩阵 * X转置矩阵 * Y 
	X为m*n的矩阵，m表示样本组的数量，n表示每个样本的特征，特征1，特征2...特征n
	Y为m*1的向量，m为每个样本组对应的正确结果，
	octave版本： a = pinv(A'*A)*A'*Y

	DEMO
	# X = np.mat([[1, 0], [1, 1], [1, 2]])
	# Y = np.mat([[1], [2], [3]])
	# a = lineAlgorithm(X, Y)
	# print(X)
	# print(Y)
	# print(a)

	# #pridict
	# P = np.mat([[1, 3], [1, 4]])
	# print(P*a)
	'''
	return (X.T * X).I * X.T * Y

def getXYdata():
	Xdata = []
	Ydata = []
	gameSession = ['13_14', '14_15', '15_16', '16_17'];
	for i in range(0, len(gameSession)):
		sql = "SELECT * FROM nba_match_data_{session} limit 1300".format(session = gameSession[i])
		data = db.find(sql)
		if len(data) > 0:
			for j in range(0, len(data)):
				Xtemp = []
				Ytemp = []
				Xtemp = [
				data[j]['is_host'], 
				data[j]['FG'], 
				# data[j]['FGA'], 
				data[j]['3P'], 
				# data[j]['3PA'], 
				# data[j]['FT'], 
				# data[j]['FTA'], 
				# data[j]['ORB'], 
				# data[j]['DRB'], 
				# data[j]['TRB'], 
				# data[j]['AST'], 
				# data[j]['STL'], 
				# data[j]['BLK'], 
				data[j]['FG%'], 
				data[j]['3P%']]
				Xdata.append(Xtemp)

				Ytemp = [data[j]['PTS']]
				Ydata.append(Ytemp)

	result = {'x':Xdata, 'y':Ydata}
	return result		

def getPridictionMatch(session, matchId):
	'''输入比赛ID，获取主客队的预测数据，根据分别的主客场前五场平均数据作为预测输入数据'''
	result = {'host':[], 'guest':[]}

	matchInfoSql = "SELECT *,FROM_UNIXTIME(match_time) from nba_match_list_{session} where match_id={matchId} limit 1".format(session = session, matchId = matchId)
	matchInfo = db.find(matchInfoSql)
	if len(matchInfo)<=0:
		print('该比赛不存在');exit()
	
	hostPridictionSql = "select CAST(sum(FG)/5 as SIGNED) as FG,CAST(sum(3P)/5 as SIGNED) AS 3P,CAST(sum(FT)/5 as SIGNED) as FT,ceil(sum(`FG%`)/5) as 'FG%',ceil(sum(`3P%`)/5) as '3P%' from (select *,FROM_UNIXTIME(match_time) from nba_match_data_{session} where team_id={team_id} limit 5) as a;".format(session = session, team_id = matchInfo[0]['host_id'])
	hostPridictionData = db.find(hostPridictionSql)
	guestPridictionSql = "select CAST(sum(FG)/5 as SIGNED) as FG,CAST(sum(3P)/5 as SIGNED) AS 3P,CAST(sum(FT)/5 as SIGNED) as FT,ceil(sum(`FG%`)/5) as 'FG%',ceil(sum(`3P%`)/5) as '3P%' from (select *,FROM_UNIXTIME(match_time) from nba_match_data_{session} where team_id={team_id} limit 5) as a;".format(session = session, team_id = matchInfo[0]['guest_id'])
	guestPridictionData = db.find(guestPridictionSql)
	
	result['host'].append(1)
	result['host'].append(hostPridictionData[0]['FG'])
	result['host'].append(hostPridictionData[0]['3P'])
	# result['host'].append(hostPridictionData[0]['FT'])
	result['host'].append(hostPridictionData[0]['FG%'])
	result['host'].append(hostPridictionData[0]['3P%'])

	result['guest'].append(0)
	result['guest'].append(guestPridictionData[0]['FG'])
	result['guest'].append(guestPridictionData[0]['3P'])
	# result['guest'].append(guestPridictionData[0]['FT'])
	result['guest'].append(guestPridictionData[0]['FG%'])
	result['guest'].append(guestPridictionData[0]['3P%'])
		
	return result

def pridictScore(teamPridictionData, algorithmResultMatrix):
	'''预测球队比分'''
	teamPridictionData = np.matrix(teamPridictionData)
	return teamPridictionData * algorithmResultMatrix

def getDayMatch(begin, end):
	sql = "SELECT * FROM nba_match_list_{0} WHERE match_time between UNIX_TIMESTAMP('{1}') and UNIX_TIMESTAMP('{2}')".format(pridiction_session, begin, end)
	matchList = db.find(sql)
	return matchList

def isWin(matchInfo, pridictionHostScore, pridictionGuestScore):

	if pridictionHostScore > pridictionGuestScore and matchInfo['host_score'] > matchInfo['guest_score']:
		return True
	elif pridictionHostScore < pridictionGuestScore and matchInfo['host_score'] < matchInfo['guest_score']:
		return True
	else:
		return False

def isDiscard(matchInfo, pridictionHostScore, pridictionGuestScore):
	if pridictionHostScore > pridictionGuestScore and matchInfo['handicap']<0:
		return True;
	elif pridictionHostScore < pridictionGuestScore and matchInfo['handicap']>0:
		return True;
	else:
		return False;
####################################### main() #######################################

def main():
	'''使用线性回归预测比赛两个队的比分，训练数据为gameSession变量'''
	#获取计算最优解所需数据
	result = getXYdata()
	X = np.matrix(result['x'])
	Y = np.matrix(result['y'])
	#计算最优解
	algorithmResultMatrix = linearRegressionNormal.main(X, Y)

	#获取等待预测的比赛
	matchBeginTime 	= '2018-3-31'
	matchEndTime 	= '2018-4-1'
	# matchBeginTime  = time.strftime('%Y-%m-%d', time.localtime(time.time()+86400))
	# matchEndTime    = time.strftime('%Y-%m-%d', time.localtime(time.time()+86400*2))
	matchList = getDayMatch(matchBeginTime, matchEndTime)
	if len(matchList)<=0:
		print('所选日期没有比赛')

	#开始预测比分
	print('pridiction {0} matches.'.format(len(matchList)));
	pridictionSuccess = 0;
	pridictionFailed = 0;
	discard = 0;
	for i in range(0, len(matchList)):
		pridictionData = getPridictionMatch(pridiction_session, matchList[i]['match_id'])
		hostScore = pridictScore(pridictionData['host'], algorithmResultMatrix)
		guestScore = pridictScore(pridictionData['guest'], algorithmResultMatrix)

		print("match id:{0}, match_time:{1}".format(matchList[i]['match_id'], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(matchList[i]['match_time']))))
		print("host name: {0}, pridict score:{1}".format(matchList[i]['host_name'], hostScore))
		print("guest name: {0}, pridict score:{1}".format(matchList[i]['guest_name'], guestScore));
		print(" ");

		if isDiscard(matchList[i], hostScore, guestScore):
			discard += 1
			continue;

		if isWin(matchList[i], hostScore, guestScore):
			pridictionSuccess += 1
		else:
			pridictionFailed += 1

	# print("pridiction success:{0}, lose:{1}, discard:{2}, successPercent:{3}%".format(pridictionSuccess, pridictionFailed, discard, round(pridictionSuccess*100/(pridictionFailed+pridictionSuccess), 2)))

main()



# X = np.mat([[1.1, 0], [1, 1], [1, 2]])
# Y = np.mat([[1], [2], [3]])
# a = lineAlgorithm(X, Y)
# print([[1.1, 0], [1, 1], [1, 2]])
# print(X)
# print(Y)
# print(a)

# #pridict
# P = np.mat([[1, 3], [1, 4]])
# print(P*a)

# 欧赔低赔一方，实际欧赔大于预测欧赔0.3以上，不考虑


