from src.kostalplenticore import connect as kostalplenticoreconnect
import json
from tabulate import tabulate

# Opening JSON config file
confFile = open('config.json',)

# returns JSON object as
# a dictionary
config = json.load(confFile)

# Connect
con = kostalplenticoreconnect(config['host'], config['password'])
con.login()

# Create table
table = [
        # Battery
        ["Battery SoC",con.getBatteryPercent(),"%"],
        ["Battery cycles",con.getBatteryCycles(),""],
        # Power
        ["Home Power",con.getHomePowerConsumption(),"W"],
        ["PV Power",con.getPvPower(),"W"],
        ["Grid Power",con.getGridPower(),"W"],
        ["Battery Power",con.getBatteryPower(),"W"],
        # Energy
        ["Home energy usage",con.getHomeConsumptionTotal(),"kWh"],
        ["Home energy usage from grid",con.getHomeConsumptionFromGridTotal(),"kWh"],
        ["Home energy usage from PV",con.getHomeConsumptionFromPVTotal(),"kWh"],
        ["Home energy usage from battery",con.getHomeConsumptionFromBatTotal(),"kWh"],
        # Voltage
        ["Voltage 3P average",con.getAcVoltage3pAvg(),"V"]
        ]

print(tabulate(table))