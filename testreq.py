from src.kostalplenticore import connect as kostalplenticoreconnect
import json

# Opening JSON config file
confFile = open('config.json',)

# returns JSON object as 
# a dictionary
config = json.load(confFile)


con = kostalplenticoreconnect(config['host'], config['password'])
con.login()
print(con.getBatteryPercent())
print(con.getPvPower())
print(con.getHomePowerConsumption())
print(con.getProcessdata("devices:local", ["HomeGrid_P"])[0]["value"])
