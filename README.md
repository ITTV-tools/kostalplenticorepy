# KostalPlenticore-Python
Python library to request data from Kostal Plenticore Plus

Special thanks to E3EAT

Usage:

```python
<<<<<<< HEAD
import kostalpy

con = kostalpy.connect("192.168.1.23", "Password")
=======
import kostalplenticore

con = kostalplenticore.connect("192.168.251.22", "Password")
>>>>>>> 517e78bcf93f935d63181b6060a6be6219d486dd
con.login()
print(con.getBatteryPercent())
print(con.getPvPower())
print(con.getHomePowerConsumption())
<<<<<<< HEAD
=======
print(con.getProcessdata("devices:local", ["HomeGrid_P"])[0]["value"])
>>>>>>> 517e78bcf93f935d63181b6060a6be6219d486dd

```
