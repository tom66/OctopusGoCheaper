# Do not publicly disclose these!
APIKEY = 'sk_live_Z8PlNAqEU2mQi0deODCBxoDM'
MPT = '2400000226176'
METER = '20L3253341'

# Change this to point to the file that represents your Agile CSV data for your region
# You can download these files here: https://www.energy-stats.uk/download-historical-pricing-data/ (not affiliated!)
AGILE_CSV_FILE = 'csv_agile_A_Eastern_England.csv'

# Set up your offpeak and onpeak settings for Go Faster here
# The example below is for Octopus Go Faster 2030 5H v1,  inclusive of 1.30am  (1am -> 1.30am end)
# Each bin is a half-hour long
OFFPEAK_TIMES = [ 20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5, 0.0, 0.5, 1.0 ]  
OFFPEAK_RATE = 5.5
ONPEAK_RATE = 14.12
