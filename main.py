#!/usr/bin/python
# -*- coding: utf-8 -*-

from DemoEventsJoin.app import *


def main():
    """Main function.
    1) Process the arguments to the script.Generates help for script
    2) Sets up Output directory
    3) Loads data (with patient_id as key) & headers of demo.psv and events.psv
    4) Gets the common 'patient_id' keys between the two datasets
    5) Join data by looping through common key 'patient_id'
    6) Performs Sanity Checks on demo and events data
    7) Creates JSON if sanity checks passes and non-zero events present
    8) Measure the following statistics:
        a) Total No. of Valid patients
        b) Max/Min/Median length of patient timelines in days
        c) Count of males and females
        d) Max/Min/Median age of patient as b/w  birthdate and last event"""

    # Process the arguments to the script.Generates help for script

    args = ProcessArgs(sys.argv[1:], 'Join Script for demo.psv and events.psv')

    # Sets up Output directory

    folder_name = SetOutputDirectory(args)

    # Loads data with 'patient_id' as key & headers of demo.psv and events.psv

    (demo_header, demo_dict) = LoadPsvFile(args.demo, 'patient_id', 0)
    (events_header, events_dict) = LoadPsvFile(args.events, 'patient_id', 1)

    # Gets the common 'patient_id' keys between the two datasets

    keys_for_demo = set(demo_dict.keys())
    keys_for_events = set(events_dict.keys())
    common_keys = keys_for_demo.intersection(keys_for_events)

    # Join data by looping through common key 'patient_id'

    # Initializing the Variables to store the statistics

    total_valid_patients = 0
    patient_timeline = []
    count_males = 0
    count_females = 0
    patient_age = []

    for key_val in common_keys:
        demo_row = demo_dict[key_val]

        # Performs Sanity Checks on demo row. Skip invalid rows

        if IsInvalidDemo(demo_row, demo_header):
            continue

        # Filter Event rows if they contain invalid data

        events_row = FilterEvents(events_dict[key_val], events_header)
        if len(events_row) != 0:
            CreateJson(folder_name, demo_row, events_row, demo_header,
                       events_header)

            # Measuring statistics

            total_valid_patients += 1

            patient_timeline.append(GetPatientTimeline(events_row,
                                    events_header))

            if IsPatientMale(demo_row, demo_header):
                count_males += 1
            else:
                count_females += 1

            patient_age.append(GetPatientAge(demo_row, demo_header,
                               events_row, events_header))

    # Sort the patient age and patient timeline

    patient_age.sort()
    patient_timeline.sort()

    print '-----------------------------------------------------------------'
    print 'Total number of valid patients is %d' % total_valid_patients
    print 'Length of patient timeline: Maximum = %d' % patient_timeline[-1]
    print 'Length of patient timeline: Minimun = %d' % patient_timeline[0]
    print 'Length of patient timeline: Median = %f' \
          % GetMedian(patient_timeline)
    print 'Count of males is %d and females is %d' \
          % (count_males, count_females)
    print 'Length of patient age: Maximum = %d' % patient_age[-1]
    print 'Length of patient age: Minimun = %d' % patient_age[0]
    print 'Length of patient age: Median = %f' % GetMedian(patient_age)
    print '-----------------------------------------------------------------'


if __name__ == '__main__':
    main()
