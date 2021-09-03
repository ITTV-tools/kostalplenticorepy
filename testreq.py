from src.kostalplenticore import connect as kostalplenticoreconnect
import json

# Opening JSON config file
confFile = open('config.json',)

# returns JSON object as
# a dictionary
config = json.load(confFile)


con = kostalplenticoreconnect(config['host'], config['password'])
con.login()
print('Battery:     ' + str(con.getBatteryPercent()) + " %")
print('PV Power:    ' + str(con.getPvPower()) + " W")
print('Home Power:  ' + str(con.getHomePowerConsumption()) + " W")
print('Grid Power:  ' + str(con.getProcessdata("devices:local",
      ["HomeGrid_P"])[0]["value"]) + " W")
