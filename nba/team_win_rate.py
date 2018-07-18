import sys
sys.path.append("..")
import db.db as db
import matplotlib.pyplot as plt

db = db.Db()

sql = "select * from nba_team where tid=7 limit 10"
teamList = db.find(sql)

def get_data(teamId):
	match_result = []
	sql 	= "select *,FROM_UNIXTIME(match_time) from nba_match_list_15_16 where host_id="+str(teamId)+" or guest_id="+str(teamId)
	data 	= db.find(sql)

	for value in data:
		if ((value['host_id'] == teamId) & (value['host_score'] > value['guest_score'])):
			match_result.append(1)
		elif((value['guest_id'] == teamId) & (value['guest_score'] > value['host_score'])):
			match_result.append(1)
		else:
			match_result.append(-1)

	return match_result

def draw_win(teamList):
	'''绘制球队胜负情况'''
	total_match_result = []
	plt.figure(figsize=(15,7))

	i = 1
	for team in teamList:
		match_result = get_data(team['tid'])
		plt.subplot(len(teamList), 1, i)

		x = list(range(1, len(match_result)+1))
		y = match_result

		plt.plot(x, y, 'r-p')
		plt.grid()
		plt.ylabel(team['tid'])

		i = i+1

	plt.show()

def cal_rate(match_list):
	'''计算某个队的每场比赛的赢率'''
	win_rate = []
	single_team_win_odds_rate = current_win = current_lose = current_total = 0
	for v1 in match_list:
		if v1 == 1:
			current_win = current_win + 1
		elif v1 == -1:
			current_lose= current_lose+ 1
		current_total = current_total + 1

		win_rate.append(round(current_win*100/current_total, 2))
	
	return win_rate

def draw_win_percent(teamList):
	total_match_result = []
	plt.figure(figsize=(15,7))

	i = 1
	for team in teamList:
		match_result = get_data(team['tid'])
		rate = cal_rate(match_result)

		plt.subplot(len(teamList), 1, i)

		x = list(range(1, len(match_result)+1))
		y = rate

		plt.plot(x, y, 'r-p')
		plt.grid()
		plt.ylabel(team['tid'])
		plt.ylim(0, 100)

		i = i+1

	plt.show()


# draw_win(teamList)
draw_win_percent(teamList)



