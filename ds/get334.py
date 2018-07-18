
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

def getData():
	
	url = 'https://live.dszuqiu.com/ajax/score/data'

	data = {'mt':currentTime}
	getResult = requests.get(url, params = data)

	return getResult.text

def doData(resultString):
	resultJson = json.loads(resultString)
	matchList = resultJson['rs']
	for i in range(0, len(matchList)):
		matchData = matchList[i]
		if 'events_graph' in matchData.keys():
			events = matchData['events_graph']['events']
			if len(events) > 0:
				doAnalyse(matchData, events)
		else:
			continue


def doAnalyse(matchData, eventList):
	matchId = matchData['id']
	leagueName = matchData['league']['n']
	hostName 	= matchData['host']['stn']
	guestName 	= matchData['guest']['stn']

	hostGoalNum = 0;
	guestGoalNum= 0;

	if filterLeague(leagueName) == False:
		return

	for i in range(0, len(eventList)):

		t = eventList[i]['t']
		status = int(eventList[i]['status'])
		if status<30:
			if t == 'hg':
				hostGoalNum += 1;
			elif t == 'gg':
				guestGoalNum+= 1;

	if (hostGoalNum + guestGoalNum) >= 3:
		insertData(matchId, leagueName, hostName, guestName, hostGoalNum, guestGoalNum)


def insertData(matchId, leagueName, hostName, guestName, hostGoalNum, guestGoalNum):
	sql = "SELECT count(*) as num FROM ds_push WHERE match_id={matchId}".format(matchId = matchId)
	data = db.find(sql)
	num = data[0]['num']
	if num == 0:
		keys = ['match_id', 'league_name', 'host_name', 'guest_name', 'host_goal_num', 'guest_goal_num', 'created_at'];
		values = [[matchId, leagueName, hostName, guestName, hostGoalNum, guestGoalNum, currentTime]];
		db.insertBatch('ds_push', keys, values)


def push():
	sql = "SELECT * from ds_push where is_push=0";
	pushData = db.find(sql)

	mailTitle = '334规则'
	mailContent = ''
	pushIds = []
	for i in range(0, len(pushData)):
		tmpContent = pushData[i]['league_name'] + "\r\n<br>" + pushData[i]['host_name'] + "（" + str(pushData[i]['host_goal_num']) + "）：（" + str(pushData[i]['guest_goal_num']) + "）" + pushData[i]['guest_name'] + "\r\n<br>"
		mailContent = tmpContent + mailContent
		pushIds.append(str(pushData[i]['match_id']))

	if pushIds:
		updateSql = "UPDATE ds_push SET is_push=1 WHERE match_id in (" + str(','.join(pushIds)) + ")"
		db.update(updateSql)

		historySql = "SELECT * FROM ds_push order by id desc limit 20"
		historyData = db.find(historySql)
		historyContent = "\r\n<br>\r\n<br>历史记录\r\n<br>"
		if historyData:
			for k in range(0, len(historyData)):
				status = ''
				result = historyData[k]['result']
				if str(result) == '0':
					status = '<span style="color:#FFB848">未结算</span>'
				elif str(result) == '1':
					status = '<span style="color:red">红</span>'
				elif str(result) == '-1':
					status = '<span style="color:black">黑</span>'
				else:
					status = '未知错误'
				tmp = "          " + historyData[k]['league_name'] + "\r\n<br>(" + status + ")---" + historyData[k]['host_name'] + historyData[k]['guest_name'] + "\r\n<br>"
				
				historyContent = historyContent + tmp
		mailContent += historyContent
		mail(mailTitle, mailContent)

def mail(mailTitle, mailContent):
    ret=True
    my_sender='1493943799@qq.com'    # 发件人邮箱账号
    my_pass = 'tlnsijddqzdggjef'              # 发件人邮箱密码
    my_user='1493943799@qq.com'      # 收件人邮箱账号，我这边发送给自己
    try:
	    msg=MIMEText(mailContent,'html','utf-8')
	    msg['From']=formataddr(["allen's python script",my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
	    msg['To']=formataddr(["allen",my_user])              # 括号里的对应收件人邮箱昵称、收件人邮箱账号
	    msg['Subject']=mailTitle                # 邮件的主题，也可以说是标题

	    server=smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
	    server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
	    server.sendmail(my_sender,[my_user,],msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
	    server.quit()  # 关闭连接
    except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret=False
    return ret

def filterLeague(leagueName):
	if (leagueName[:3] == '俄罗斯') or (leagueName[:3] == '乌克兰'):
		return False
	else:
		return True
		

def updateResult(resultString):
	beforeTime = int(time.time()) - 86400*2
	needUpdateSql = "SELECT match_id FROM ds_push WHERE result=0 and created_at>{beforeTime}".format(beforeTime = beforeTime)
	needUpdateData= db.find(needUpdateSql)
	if len(needUpdateData) <= 0:
		return

	resultJson = json.loads(resultString)
	matchList = resultJson['rs']
	for i in range(0, len(matchList)):
		matchData = matchList[i]
		events = matchData['events_graph']['events']
		matchId = matchData['id']

		tmp = False
		for k in range(0, len(needUpdateData)):
			if str(matchId) == str(needUpdateData[k]['match_id']):
				tmp = True

		if tmp == False:
			continue

		num = 0;
		if events:
			for j in range(0, len(events)):
				t = events[j]['t']
				status = events[j]['status']
				if ((t == 'gg') or (t == 'hg')) and int(status) <= 45:
					num += 1
			
			if num >= 4:
				updateResult = 1
			else:
				updateResult = -1

			updateSql = "UPDATE ds_push SET result={updateResult} WHERE match_id={matchId}".format(updateResult = updateResult, matchId = matchId)
			db.update(updateSql)



currentTime = int(time.time())
db = db.Db('ds')
data = getData()
# updateResult(data)
doData(data)
push()



