import requests
import pprint
import datetime
from dateutil import parser
import sys
import csv
from Settings import *  # You will need to edit Settings.py

print("Loading Agile CSV Data...")

csv_fp = open(AGILE_CSV_FILE, 'r')
csv_data = csv.reader(csv_fp)

agile_tariff_prices = {}
    
for row in csv_data:
    agile_tariff_prices[parser.parse(row[0])] = float(row[4])

csv_fp.close()

print("Downloading your Usage Data...")

url = 'https://api.octopus.energy/v1/electricity-meter-points/' + MPT + '/meters/' + METER + '/consumption/?page_size=25000'
r = requests.get(url, auth=(APIKEY,''))
output_dict = r.json()

print("Creating Summary...")

total_consumption_offpeak = 0
total_consumption_onpeak = 0

consumption_bins = {}
agile_cost_bins = {}
go_cost_bins = {}

for i in range(48):
    consumption_bins[i] = 0.0
    go_cost_bins[i] = 0.0
    agile_cost_bins[i] = 0.0

hfracs = 0
max_kWh_in_bin = 0.0
max_kWh_starttime = None

agile_total_cost = 0.0

now = datetime.datetime.now(datetime.timezone.utc)

for line in output_dict['results']:
    dt = parser.parse(line['interval_start'])
    
    # convert hours to half-fraction representation
    hour_frac = (dt.hour + (dt.minute / 60))
    hour_frac *= 2
    hour_frac = int(hour_frac)
    
    consumption_bins[hour_frac] += line['consumption']
    hfracs += 1
    
    if (now - dt).days < 90 and line['consumption'] > max_kWh_in_bin:
        max_kWh_in_bin = line['consumption']
        max_kWh_starttime = line['interval_start']
    
    if (hour_frac / 2) in OFFPEAK_RATE:
        total_consumption_offpeak += line['consumption']
        go_cost_bins[hour_frac] += OFFPEAK_RATE * line['consumption']
    else:
        total_consumption_onpeak += line['consumption']
        go_cost_bins[hour_frac] += ONPEAK_RATE * line['consumption']
    
    try:
        agile_cost = agile_tariff_prices[dt] * line['consumption']
    except KeyError:
        print("No Agile pricing for", dt)
    else:
        agile_total_cost += agile_cost
        agile_cost_bins[hour_frac] += agile_cost

days = hfracs / 48

total_consumption = total_consumption_onpeak + total_consumption_offpeak
        
total_cost_offpeak = total_consumption_offpeak * OFFPEAK_RATE * 0.01    # Caclulate in pounds
total_cost_onpeak = total_consumption_onpeak * ONPEAK_RATE * 0.01

agile_total_cost *= 0.01

print("")
print("Total OFF-PEAK:                    %.2f kWh" % total_consumption_offpeak)
print("Total ON-PEAK:                     %.2f kWh" % total_consumption_onpeak)
print("Total usage:                       %.2f kWh" % total_consumption)
print("Percentage OFF-PEAK:               %.2f%%"   % ((total_consumption_offpeak / total_consumption) * 100))
print("")
print("Total OFF-PEAK cost:               £%.2f" % total_cost_offpeak)
print("Total ON-PEAK cost:                £%.2f" % total_cost_onpeak)
print("Total cost:                        £%.2f" % (total_cost_onpeak + total_cost_offpeak))
print("Comparable Agile cost*:            £%.2f (*assumes no behaviour adjustment)" % (agile_total_cost))
print("")
print("Max. power in last 90 days:        %.3f kW" % (max_kWh_in_bin * 2.0))
print("Achieved on date:                  %s" % max_kWh_starttime)
print("")
print("*** Summary of average consumption ***")
print("")

max_kw = max(consumption_bins.values()) * (1.0 / days) * 2.0
bar_scale = 90

#print(max_kw, max(consumption_bins.values()), consumption_bins)

print("Time   .....   Power  ", ' ' * bar_scale, "     Agile Cost    GoFast. Cost   Delta")
      
for i in range(48):
    kw = consumption_bins[i] * (1.0 / days) * 2.0
    f = (kw / max_kw)
    graph = ('*' * int(bar_scale * f)) + (' ' * (bar_scale - int(bar_scale * f)))
    agile, go_fast = agile_cost_bins[i] * 0.01, go_cost_bins[i] * 0.01
    
    print("\033[0m%02d:%02d  .....  %6.3f kW (%s)   £%6.2f       £%6.2f        " % (i / 2, (i % 2) * 30, kw, graph, agile, go_fast), end='')
    
    if (agile > go_fast):
        print("\033[92m£%6.2f" % (go_fast - agile))
    else:
        print("\033[91m£%6.2f" % (go_fast - agile))

    