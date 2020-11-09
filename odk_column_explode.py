#!/usr/bin/env python3

import csv
import re
import sys
import os
import pprint

# { columnName: set([all, numbers, seen])}
UNIQUE_NUMBERS = {}

DELIMITER = ":" #sometimes it's a : and sometimes a -
# this gets updated later

# if you want to use different values, you can do so by putting in higher values here
# this dictionary comes from line 114 below

variableCount = {
    "activities": 6,
    "animaltype": 6,
    "aware": 6,
    "change": 2,
    "clean": 2,
    "color": 6,
    "condition": 2,
    "croptype": 28,
    "endline": 5,
    "enter": 5,
    "environment": 4,
    "fruittype": 11,
    "health": 6,
    "hhprot": 4,
    "impact": 8,
    "item": 9,
    "material": 4,
    "mobility": 2,
    "occ": 26,
    "painttype": 6,
    "personalprot": 3,
    "places": 4,
    "play": 5,
    "relationship": 10,
    "sampletype": 8,
    "scraps": 4,
    "ulab": 6,
    "ulabactiv": 7,
    "water": 12,
    "ways": 10,
}

columnToVariable = {
    "act": "activities",
    "animals": "animaltype",
    "how": "aware",
    "c1change": "change",
    "c2change": "change",
    "cleanin": "clean",
    "cleanout": "clean",
    "color": "color",
    "cond": "condition",
    "crops": "croptype",
    "consent": "endline",
    "bod": "enter",
    "env": "environment",
    "fruits": "fruittype",
    "c1symptom": "health",
    "c2symptom": "health",
    "enter": "hhprot",
    "hum": "impact",
    "items": "item",
    "in": "material",
    "out": "material",
    "wall": "material",
    "c1mobile": "mobility",
    "hohocc": "occ",
    "occ": "occ",
    "occprecovid": "occ",
    "paint": "painttype",
    "ppe": "personalprot",
    "proc": "places",
    "c1play": "play",
    "c2play": "play",
    "relation": "relationship",
    "collect": "sampletype",
    "observe": "scraps",
    "jobs": "ulab",
    "c1playulab": "ulabactiv",
    "c1ulabact": "ulabactiv",
    "c2playulab": "ulabactiv",
    "c2ulabact": "ulabactiv",
    "cplayulab": "ulabactiv",
    "inhome": "ulabactiv",
    "wat": "water",
    "avoid": "ways",
}

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

# all columns
COLUMNS = []
# all columns with xxx:yyy: prefixes removed
CORRECTED_COLUMNS = []

# all in input rows, minus : prefixes
CORRECTED_ROWS = []

if len(sys.argv) < 3:
    exit("Please specify an input and output filename")

inputName = sys.argv[1]
outputName = sys.argv[2]

__location__ = os.path.realpath(os.path.join(
    os.getcwd(), os.path.dirname(__file__)))
filePath = os.path.join(__location__, inputName)
if not os.path.exists(filePath):
    exit("Could not find file: " + inputName)

# get the max integer for a string delimited set


def get_max(inputString):
    return max([int(x) for x in inputString.split(' ')])


def needs_splitting(inputString):
    return re.match('^[0-9 ]+$', inputString) and ' ' in inputString


def is_numeric(inputString):
    if not inputString:
        return False
    return re.match('^[0-9 ]+$', inputString)

def col_name(colName, numVal):
    return colName + "-" + str(numVal)


# iterate through the csv to ingest the space-delimited values
with open(filePath, 'r') as inputFile:
    reader = csv.DictReader(inputFile)
    data = {}
    ignore = set([])
    COLUMNS = reader.fieldnames
    # get the right delimiter
    if DELIMITER not in "".join(COLUMNS):
        DELIMITER = "-"
    if DELIMITER not in "".join(COLUMNS):
        print("Failed to determine correct colunm name delimiter!")
        sys.exit()

    CORRECTED_COLUMNS = [x.split(DELIMITER)[-1] for x in COLUMNS]
    for row in reader:
        # save each row (as a dictionary) for writing later
        CORRECTED_ROWS.append({k.split(DELIMITER)[-1]: v for (k, v) in row.items()})
        for header, value in row.items():
            if is_numeric(value):
                values = [int(x) for x in value.split(" ")]
                UNIQUE_NUMBERS[header] = UNIQUE_NUMBERS.get(
                    header, set([])).union(values)

# insert rowname-number columns for each potential value
"""
for key, value in UNIQUE_NUMBERS.items():
    if key not in MULTIPLE_NUMBERS:
        continue
    additionalItems = [col_name(key, x) for x in range(1, max(value) + 1)]
    ind = COLUMNS.index(key) + 1
    COLUMNS[ind:ind] = additionalItems
"""

# get max variable number per column
columnToMaxNumber = {k: variableCount[v]
                     for (k, v) in columnToVariable.items()}

for key, value in columnToMaxNumber.items():
    additionalItems = [col_name(key, x) for x in range(1, value + 1)]
    # Note; some of the keys in the final versions aren't in the first version
    if key in CORRECTED_COLUMNS:
        ind = CORRECTED_COLUMNS.index(key) + 1
        CORRECTED_COLUMNS[ind:ind] = additionalItems
    else:
        print("Missing column: " + key)

# print header, max of each column with multiple items
"""
seed = {}
print("Max number values for columns:")
for column in MULTIPLE_NUMBERS:
    seed[column] = max(UNIQUE_NUMBERS[column])
pprint.pprint(seed)
"""

with open(outputName, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=CORRECTED_COLUMNS)
    writer.writeheader()

    for row in CORRECTED_ROWS:
        outputRow = row.copy()
        for key, value in row.items():
            if key in columnToMaxNumber.keys():
                values = value.split(" ")
                if 'other' in values:
                    # sometimes there's an "other" field which can be mixed in with numbers
                    values.remove('other')
                for x in values:
                    if (x != ''):
                        outputRow[col_name(key, x)] = 1

        writer.writerow(outputRow)
    print("Wrote output to " + outputName)
