#!/usr/bin/env python3

import csv, re, sys, os, pprint

# { columnName: set([all, numbers, seen])}
UNIQUE_NUMBERS = {}

# if you want to use different values, you can do so by putting in higher values here
MAX_VALUES = \
{'child:c1change': 2,
 'child:c1mobile': 2,
 'child:c1play': 5,
 'child:c1symptom': 6,
 'child:c1ulabact': 7,
 'child:c2child:c2play': 5,
 'child:c2child:c2symptom': 6,
 'child:c2child:c2ulabact': 7,
 'consent': 4,
 'demo:hohocc': 26,
 'demo:items': 9,
 'demo:occ': 24,
 'demo:occprecovid': 23,
 'food:animals': 6,
 'food:crops': 28,
 'food:fruits': 11,
 'food:proc': 3,
 'food:wat': 10,
 'hhchar:cleanin': 2,
 'hhchar:color': 6,
 'hhchar:paint': 6,
 'hhchar:wall': 4,
 'knowledge:avoid': 7,
 'knowledge:bod': 5,
 'knowledge:env': 4,
 'knowledge:hum': 8,
 'samples:collect': 8,
 'soilpb:c1playulab': 7,
 'soilpb:c2playulab': 7,
 'soilpb:cplayulab': 7,
 'ulab:act': 6,
 'ulab:enter': 4,
 'ulab:how': 6,
 'ulab:inhome': 7,
 'ulab:jobs': 6,
 'ulab:ppe': 3,
 'ulab:relation': 8}

# Uncomment if you want to use the above max values:
"""
if MAX_VALUES:
    for key, value in MAX_VALUES.items():
        UNIQUE_NUMBERS[key] = set([value])
"""

# column names with muliple numbers
MULTIPLE_NUMBERS = set([])

# column names
COLUMNS = []

INPUT_ROWS = []

if len(sys.argv) < 2:
    exit("Please specify a filename")

fname = sys.argv[1]

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
filePath = os.path.join(__location__, fname)

if not os.path.exists(filePath):
    exit("Could not find file: " + fname)

# get the max integer for a string delimited set
def get_max(inputString):
    #print(repr(inputString))
    return max([int(x) for x in inputString.split(' ')])

def needs_splitting(inputString):
    return re.match('^[0-9 ]+$', inputString) and ' ' in inputString

def is_numeric(inputString):
    return re.match('^[0-9 ]+$', inputString)

def col_name(colName, numVal):
    return colName + "-" + str(numVal)

# iterate through the csv to find the max nubmer per string delimited rows
with open(filePath,'r') as tsvin:
    reader = csv.DictReader(tsvin)
    data = {}
    ignore = set([])
    COLUMNS = reader.fieldnames
    for row in reader:
        # save each row (as a dictionary) for writing later
        INPUT_ROWS.append(row)
        for header, value in row.items():
            if is_numeric(value):
                values = [int(x) for x in value.split(" ")]
                if len(values) > 1:
                   MULTIPLE_NUMBERS.add(header)
                UNIQUE_NUMBERS[header] = UNIQUE_NUMBERS.get(header, set([])).union(values)
    #print(UNIQUE_NUMBERS)
    #print(ignore)

# insert rowname-number colums for each potential value
for key, value in UNIQUE_NUMBERS.items():
    if key not in MULTIPLE_NUMBERS:
        continue
    additionalItems = [col_name(key, x) for x in range(1, max(value) + 1)]
    ind = COLUMNS.index(key) + 1
    COLUMNS[ind:ind] = additionalItems

# print header, max of each column with multiple items
seed = {}
print("Max number values for colums:")
for column in MULTIPLE_NUMBERS:
    seed[column] = max(UNIQUE_NUMBERS[column])
pprint.pprint(seed)

with open('output.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=COLUMNS)
    writer.writeheader()

    for row in INPUT_ROWS:
        outputRow = row.copy()
        for key, value in row.items():
            if key in MULTIPLE_NUMBERS and value != "":
                values = value.split(" ")
                if 'other' in values:
                    values.remove('other') # sometimes there's an "other" field which can be mixed in with numbers
                for x in values:
                    outputRow[col_name(key, x)] = True
        writer.writerow(outputRow)
    print("Wrote output to output.csv")