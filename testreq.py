import kostalplenticore

con = kostalplenticore.connect("192.168.251.22", "<PW>")
con.login()
print(con.getBatteryPercent())
print(con.getPvPower())
print(con.getHomePowerConsumption())
print(con.getProcessdata("devices:local", ["HomeGrid_P"])[0]["value"])
