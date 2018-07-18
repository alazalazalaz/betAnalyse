'''抓取每场赛后比赛的欧赔'''
import sys
import requests
sys.path.append("../../")
import db.db as db

session = '17_18'
matchListTable = 'nba_match_list_' + session

dbObj = db.Db('nba')

def getMatchData(matchId):
	prefix1 = str(matchId)[0:1]
	prefix2 = str(matchId)[1:3]
	url = "http://nba.win007.com/1x2/data1x2/{0}/{1}/{2}.js".format(prefix1, prefix2, matchId)
	curlData = requests.get(url)

	if len(curlData.text) < 100:
		print("该队没有数据啦,{0}".format(curlData.url));exit()

	return curlData.text

def formatData(data):
	result = {'hostOdd':'', 'guestOdd':''}
	bet365Data = ''
	wdData = ''
	wdName = '伟德(直布罗陀)'
	bet365Name = 'Bet365'

	dataArr = data.split('"');
	for i in range(0, len(dataArr)):
		if bet365Name in dataArr[i]:
			bet365Data = dataArr[i]
		if wdName in dataArr[i]:
			wdData = dataArr[i]

	result = eachCom(bet365Data, bet365Name)
	if len(result['hostOdd']) <= 0 or len(result['guestOdd']) <= 0:
		result = eachCom(wdData, wdName)

	return result

def eachCom(companyOdd, companyName):
	result = {'hostOdd':'', 'guestOdd':''}
	if len(companyOdd) < 10:
		print("{0}赔率为空, {1}".format(companyName, companyOdd))
		return result

	companyOddArr = companyOdd.split('|')
	hostOdd = companyOddArr[8]
	guestOdd = companyOddArr[9]

	if len(hostOdd) <= 0 or len(guestOdd) <= 0:
		hostOdd = companyOddArr[3]
		guestOdd = companyOddArr[4]


	result['hostOdd'] = hostOdd
	result['guestOdd']= guestOdd

	return result

def writeDb(teamId, teamOdd):
	sql = "UPDATE {table} SET host_odd={h},guest_odd={g} where match_id={id}".format(table = matchListTable,h=teamOdd['hostOdd'], \
		g = teamOdd['guestOdd'], id = teamId)
	
	dbObj.update(sql)

def doMain(teamId):

	#curl该队的赔率
	curlData = getMatchData(teamId)

	#解析赔率，匹配出365公司的赔率(即赔，如果没有，则取初赔)
	teamOdd = formatData(curlData)

	#入库
	writeDb(teamId, teamOdd)

	#log
	print("teamId:{t} 修改成功".format(t = teamId))


def getMatchList():
	sql = "SELECT * FROM {table} WHERE host_odd<=0".format(table = matchListTable)
	data = dbObj.find(sql)
	if len(data)<=0:
		print('没有比赛了哎')
	return data

def main():
	matchList = getMatchList()
	
	for i in range(0, len(matchList)):
		teamId = matchList[i]['match_id']
		doMain(teamId)

	print("over")

main()