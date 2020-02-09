# KostalPlenticore-Python
Python library to request data from Kostal Plenticore Plus

Special thanks to E3EAT



Usage:

```python
import kostalplenticore

con = kostalplenticore.connect("192.168.251.22", "Password")
con.login()
print(con.getBatteryPercent())
print(con.getPvPower())
print(con.getHomePowerConsumption())
print(con.getProcessdata("devices:local", ["HomeGrid_P"])[0]["value"])

```
Install:
pip install kostalplenticore
