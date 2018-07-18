import sys
import db as dbModule
sys.path.append("../common/")
import config.db as DbConfigModule


dbConfig = DbConfigModule.DbConfig()
config = dbConfig.getConfigs()

db = dbModule.Db('ds')
sql = "SELECT * from ds_push limit 1"
data = db.find(sql)

print(data)
