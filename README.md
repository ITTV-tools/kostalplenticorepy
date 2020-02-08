# KostalPlenticore-Python
Python Libery to request data from Kostal Plenticore Plus

Special thanks to E3EAT

Usage:

```python
import kostalpy

con = kostalpy.connect("192.168.1.23", "Password")
con.login()
print(con.getBatteriePercent())
print(con.getPvPower())
print(con.getHomePowerConsumption())

```
