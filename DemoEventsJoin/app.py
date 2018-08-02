#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import csv
import argparse
import re
import os
import errno
import json
import datetime as dt


def LoadPsv(
    file_name,
    header=False,
    DELIM='|',
        QUOTECHAR='"'):

    f = open(file_name, 'rb')
    csvReader = csv.reader(f, delimiter=DELIM, quotechar=QUOTECHAR)

    if header:
        headerLine = csvReader.next()

    data = []
    for row in csvReader:
        data.append(row)

    f.close()

    if header:
        return (headerLine, data)
    else:
        return data


def SetOutputDirectory(args):
    """Setup output directory. If cannot mkdir or path not supplied
    then use ./out
    Returns: Folder name as str"""

    # Check if path for demo.psv and events.psv have been supplied

    if not args.demo:
        raise ValueError('FILE NOT INCLUDED: Please include path  demo.psv'
                         )
    if not args.events:
        raise ValueError('FILE NOT INCLUDED: Please include path events.psv'
                         )

    # Check if path for output directory has been supplied.
    # If not then use './out' folder

    if not args.outdir:
        folder_name = './out'
    else:
        folder_name = args.outdir

    # Remove './out' folder

    if os.path.exists('./out'):
        os.system('rm -rf ./out')

    # Try making the supplied path. If not use './out' folder

    try:
        os.makedirs(folder_name)
        print 'Output Folder:', folder_name
    except OSError as e:
        print 'Cannot make the folder due to ', e, \
            '\nUsing ./out instead'
        folder_name = './out'
        os.makedirs(folder_name)
    return folder_name


def LoadPsvFile(file_name, key, dups_allow):
    """Load PSV file  with data and headers
    1) file_name: File Name
    2) key: Returns a dictinary with key as index
    3) dups_allow: Do we allow duplicate keys? (primary keys?)
    Returns header,Hashmap(Key:[row0,row1,...])"""

    (header, data) = LoadPsv(file_name, header=True, DELIM='|')

    # Index of 'key'

    key_index = header.index(key)

    datadict_bykey = dict()

    for row in data:

        # If key is not a primary key then throw exception

        if row[key_index] in datadict_bykey and dups_allow == 0:
            raise ValueError('Error: Duplicates not expected in file ' +
                             file_name)
        elif row[key_index] in datadict_bykey and dups_allow == 1:

            # If key is not expected to be  primary key
            # append the row to the list of rows associated with key.

            datadict_bykey[row[key_index]].extend([row])
        else:

            # If key is not present;insert key:row to 'datadict_bykey'

            datadict_bykey[row[key_index]] = [row]

    return (header, datadict_bykey)


def ProcessArgs(argList, name):
    """Process arguments:
    1) -demo is path to demo.psv
    2) -events is path to events.psv
    3) -outdir is path to output directory
    Returns: Namespace object with arguments"""

    parser = argparse.ArgumentParser(description=name)

    parser.add_argument('-demo', type=str, help='Path of demo.psv')
    parser.add_argument('-events', type=str, help='Path of events.psv')
    parser.add_argument('-outdir', type=str,
                        help='Output Folder for JSONs. Default folder is ./out'
                        )

    return parser.parse_args(argList)


def IsValidId(id):
    """Checks Valid ID: Regex search of for, 'id-[number]'
    Returns: bool"""

    if re.search('id-\d', id):
        return True
    return False


def IsValidDate(date):
    """Checks date
    Returns: bool"""

    try:
        dt.datetime.strptime(date, '%Y-%m-%d')
        return True
    except BaseException:
        return False


def IsValidGender(gender):
    """Checks gender
    Returns: bool"""

    if gender in ['M', 'F', 'm', 'f']:
        return True
    return False


def IsValidCodeVersion(codetype):
    """Checks if ICD code version (9 or 10
    Returns: bool"""

    if str(codetype) in ['9', '10']:
        return True
    return False


def IsValidCode(code):
    """Checks if ICD code is presen
    Returns: bool"""

    if len(code) > 0:
        return True
    return False


def IsInvalidDemo(row, demoheader):
    """Checks Missing info in demographic row:
    1) Does it have 3 columns?
    2) Does it have a Valid Id, Date & Gender ?
    Returns: bool(True if Checks Fail)"""

    row = row[0]
    IndexPatientId = demoheader.index('patient_id')
    IndexBirthDate = demoheader.index('birth_date')
    IndexGender = demoheader.index('gender')
    if isinstance(row, list) and len(row) != 3:
        return True
    if not (IsValidId(row[IndexPatientId]) and
            IsValidDate(row[IndexBirthDate]) and
            IsValidGender(row[IndexGender])):
        return True
    return False


def FilterEvents(row, eventsheader):
    """Filter events based on following checks
    We have a list of rows associated with a key.
    1) Does each row have 4 columns? Filter out valid rows
    2) Does each row have valid Id, Date, ICD Code Version,
    Valid ICD Code ? Filter out valid rows.
    3) Optional:Sort valid rows by date
    Returns: list of valid rows sorted by date"""

    IndexPatientId = eventsheader.index('patient_id')
    IndexEventDate = eventsheader.index('date')
    IndexICDVersion = eventsheader.index('icd_version')
    IndexICDCode = eventsheader.index('icd_code')

    # Does each row have 4 columns? Filter out valid rows

    filter_by_len = list(map(lambda x: len(x) == 4, row))
    filtered_list = [i for (i, v) in zip(row, filter_by_len) if v]

    # Does each row have valid Id, Date, ICD Code Version,
    # Valid ICD Code ? Filter out valid rows.

    each_row_valid = list(map(lambda x: IsValidId(x[IndexPatientId]) and
                              IsValidDate(x[IndexEventDate]) and
                              IsValidCodeVersion(x[IndexICDVersion]) and
                              IsValidCode(x[IndexICDCode]),
                              filtered_list))
    filtered_list = [i for (i, v) in zip(filtered_list, each_row_valid)
                     if v]

    # Optional:Sort valid rows by date

    filtered_list = sorted(filtered_list, key=lambda x:
                           dt.datetime.strptime(x[IndexEventDate],
                                                '%Y-%m-%d'), reverse=True)
    return filtered_list


def GetSystem(code):
    """Generate 'system' key based on ICD Code Version
    Returns: url in form of str """

    if str(code) == '9':
        return 'http://hl7.org/fhir/sid/icd-9-cm'
    if str(code) == '10':
        return 'http://hl7.org/fhir/sid/icd-10'
    raise ValueError('ICD code should be 9 or 10')


def GetEvents(eventrow, eventsheader):
    """Generates data 'events' key. The input is a list of lists.Each
    list element denotes one valid event & is now converted to dictionary
    Return: list of dictionaries with each dictionary denoting one event"""

    IndexEventDate = eventsheader.index('date')
    IndexICDVersion = eventsheader.index('icd_version')
    IndexICDCode = eventsheader.index('icd_code')
    return map(lambda x: {'date': x[IndexEventDate],
                          'system': GetSystem(x[IndexICDVersion]),
                          'code': x[IndexICDCode]}, eventrow)


def GetPatientTimeline(row, eventsheader):
    """GetPatientTimeline
    Difference in datestamps in days"""

    IndexEventDate = eventsheader.index('date')
    first_row = row[0]
    last_row = row[-1]
    return (dt.datetime.strptime(first_row[IndexEventDate], '%Y-%m-%d') -
            dt.datetime.strptime(last_row[IndexEventDate], '%Y-%m-%d')).days


def GetPatientAge(demorow, demoheader, eventsrow, eventsheader):
    """GetPatientAge
    Difference in datestamps in days"""

    IndexEventDate = eventsheader.index('date')
    IndexBirthDate = demoheader.index('birth_date')
    first_row = eventsrow[0]
    demo_row = demorow[0]
    return (dt.datetime.strptime(first_row[IndexEventDate], '%Y-%m-%d') -
            dt.datetime.strptime(demo_row[IndexBirthDate], '%Y-%m-%d')).days


def IsPatientMale(demorow, demoheader):
    """Is Patient Male?"""
    IndexGender = demoheader.index('gender')
    if demorow[0][IndexGender] in ['M', 'm']:
        return True
    else:
        return False


def GetMedian(numbers):
    """Get Median of sorted Array"""
    center = len(numbers) / 2
    if len(numbers) % 2 == 0:
        return sum(numbers[center - 1:center + 1]) / 2.0
    else:
        return numbers[center]


def CreateJson(
    directory,
    demorow,
    eventrow,
    demoheader,
        eventsheader):
    """Creates JSON file in output directory"""

    IndexBirthDate = demoheader.index('birth_date')
    IndexGender = demoheader.index('gender')
    IndexPatientId = demoheader.index('patient_id')

    # Extract patient birth date, gender, and list of
    # dictionary of valid events
    demorow = demorow[0]

    data = {'birth_date': demorow[IndexBirthDate],
            'gender': demorow[IndexGender],
            'events': GetEvents(eventrow, eventsheader)}
    file_name = directory + '/' + demorow[IndexPatientId] + '.json'

    # Generate file name equals patient_id and store json

    with open(file_name, 'w') as write_file:
        json.dump(data, write_file)
