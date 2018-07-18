
import pymysql
import common.config.db as DbConfigModule



dbConfig = DbConfigModule.DbConfig()
config = dbConfig.getConfigs()
# db = pymysql.connect('localhost', 'root', '', 'nba', charset='utf8')
# cursor = db.cursor(pymysql.cursors.DictCursor)
# team_sql = "select * from nba_team where tid=7 limit 1"
# cursor.execute(team_sql)
# teamList = cursor.fetchall()

class Db():
	'''数据库连接'''
	def __init__(self, database = 'nba'):
		self.database 	= database
		self.debug 		= True

		self.db 		= pymysql.connect(config['host'], config['user'], config['pw'], self.database, charset='utf8')
		self.cursor 	= self.db.cursor(pymysql.cursors.DictCursor)


	def find(self, sql):
		self.cursor.execute(sql)
		return self.cursor.fetchall()

	def update(self, sql):
		self.cursor.execute(sql)
		self.db.commit()
		return True

	def insertBatch(self, tableName, keys, values):
		tempValueArr = []

		strdot = ","

		fields = '(`' + "`,`".join(keys) + '`)'

		for i in range(0, len(values)):
			tempArr = []
			for j in range(0, len(values[i])):
				tempArr.append("'" + str(values[i][j]) + "'")
			tempValue = '(' + strdot.join(tempArr) + ')'
			tempValueArr.append(tempValue)
		valuesString = strdot.join(tempValueArr)

		insertSql = "INSERT INTO {table} {field} VALUES {value}".format(table=tableName, field=fields, value=valuesString)
		if self.debug == True:
			# print(insertSql);exit();
			self.cursor.execute(insertSql)
			self.db.commit()
			return True
		else:
			try:
				self.cursor.execute(insertSql)
				self.db.commit()#!!!commit is necessary!!!
				return True
			except Exception as e:
				self.db.rollback()
				return False
		










