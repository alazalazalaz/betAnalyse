# -- coding: utf-8 --
#encoding = utf-8

import pymysql
import sys
import io
import numpy as np
import matplotlib.pyplot as plt

def handicap_state(teamId, item):
	if str(item['host_id']) == teamId:
		return item['handicap_win']
	else:
		if item['handicap_win'] == 1:
			return -1
		elif item['handicap_win'] == -1:
			return 1
		else:
			return 0

def get_data(teamId, cursor):
	'''获取某个队，当前赛季的所有比赛赢盘输盘情况'''
	sql = "select *,FROM_UNIXTIME(match_time) from nba_match_list_15_16 where host_id="+teamId+" or guest_id="+teamId
	cursor.execute(sql)
	data = cursor.fetchall()

	handicap_state_list = []
	handicap_win_count = handicap_lose_count = handicap_count = 0
	for value in data:
		tmp_dic = {}
		tmp_dic[value['match_id']] = handicap_state(teamId, value)

		tmp_state = handicap_state(teamId, value)
		handicap_state_list.append(tmp_state)
		if tmp_state == 1:
			handicap_win_count += 1
		elif tmp_state == -1:
			handicap_lose_count += 1

	handicap_count = len(handicap_state_list)
	return handicap_state_list


def draw_odds(teamList, cursor):
	'''画输赢盘图，x表示比赛场次，y表示输赢盘和走盘
	由于屏幕大小原因，建议最多查询10个队'''
	plt.figure(figsize=(15,7))
	i=1;
	for value in teamList:
		teamId = str(value['tid'])
		handicap_state_list = get_data(teamId, cursor)

		x = list(range(1, len(handicap_state_list)+1))
		y = handicap_state_list
		
		plt.subplot(len(teamList), 1, i)
		plt.ylabel(teamId)
		plt.grid()
		plt.plot(x, y, 'r-d')
		i = i+1

	plt.xlabel('match times')

	plt.show()

def cal_odds(handicap_state_list):
	'''计算某个队的每场比赛的赢盘率'''
	win_rate = []
	single_team_win_odds_rate = current_win = current_lose = current_total = 0
	for v1 in handicap_state_list:
		if v1 == 1:
			current_win = current_win + 1
		elif v1 == -1:
			current_lose= current_lose+ 1
		current_total = current_total + 1

		win_rate.append(round(current_win*100/current_total, 2))
	
	return win_rate

def draw_odds_percent(teamList, cursor):
	'''画输赢盘百分比图，x表示比赛场次，y表示当前阶段该队的输赢盘百分比
	由于屏幕大小原因，建议最多查询10个队'''
	plt.figure(figsize=(15,7))
	i=1;
	for value in teamList:
		teamId = str(value['tid'])
		handicap_state_list = get_data(teamId, cursor)

		win_rate = cal_odds(handicap_state_list)
		# win_rate = win_rate[40:]

		x = list(range(1, len(win_rate)+1))
		y = win_rate
		
		plt.subplot(len(teamList), 1, i)
		plt.ylim(40, 60)
		plt.ylabel(teamId)
		plt.grid()
		plt.plot(x, y, 'r-d')
		i = i+1

	plt.xlabel('match times')

	plt.show()



db = pymysql.connect('localhost', 'root', '', 'nba', charset='utf8')
cursor = db.cursor(pymysql.cursors.DictCursor)
team_sql = "select * from nba_team where tid=7 limit 1"
cursor.execute(team_sql)
teamList = cursor.fetchall()

# draw_odds(teamList, cursor)

draw_odds_percent(teamList, cursor)






