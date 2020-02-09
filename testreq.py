import kostalplenticore

con = kostalplenticore.connect("192.168.251.22", "N0Hj9xvZf5")
con.login()
print(con.getBatteryPercent())
print(con.getPvPower())
print(con.getHomePowerConsumption())
print(con.getProcessdata("devices:local", ["HomeGrid_P"])[0]["value"])
