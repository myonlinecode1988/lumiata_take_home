#!/usr/bin/python
# -*- coding: utf-8 -*-

from DemoEventsJoin.app import *


def test_IsValidId():
    """Checking IsValidId(id) function"""

    assert IsValidId('id-123') is True
    assert IsValidId('Id-123') is False
    assert IsValidId('id-') is False
    assert IsValidId('-1') is False
    assert IsValidId('ID-1') is False


def test_IsValidDate():
    """Checking IsValidDate(date) function"""

    assert IsValidDate('2017-02-23') is True
    assert IsValidDate('2017-02-32') is False
    assert IsValidDate('2017-22-02') is False
    assert IsValidDate('02-23-2017') is False
    assert IsValidDate('2017/02/23') is False


def test_IsValidGender():
    """Checking IsValidGender(gender) function"""

    assert IsValidGender('M') is True
    assert IsValidGender('F') is True
    assert IsValidGender('m') is True
    assert IsValidGender('f') is True
    assert IsValidGender('mf') is False


def test_IsValidCodeVersion():
    """Checking IsValidCodeVersion(codetype) function"""

    assert IsValidCodeVersion('9') is True
    assert IsValidCodeVersion('10') is True
    assert IsValidCodeVersion(9) is True
    assert IsValidCodeVersion(10) is True
    assert IsValidCodeVersion('11') is False


def test_IsValidCode():
    """Checking IsValidCode(code) function
    More tests using exact Specifications needed."""

    assert IsValidCode('') is False
    assert IsValidCode('H.10') is True


def test_IsInvalidDemo():
    """Checing IsInvalidDemo
    Returns True if checks fail.Expects input as [[]] only"""

    assert IsInvalidDemo([['id-123', '2017-02-23', 'F']],
                         ['patient_id', 'birth_date', 'gender']) is False
    assert IsInvalidDemo(['id-123', '2017-02-23', 'M'],
                         ['patient_id', 'birth_date', 'gender']) is True
    assert IsInvalidDemo(['2017-02-23', 'id-123', 'M'],
                         ['birth_date', 'patient_id', 'gender']) is True
    assert IsInvalidDemo(['id-123', '2017-02-23'],
                         ['patient_id', 'birth_date', 'gender']) is True


def test_FilterEvents():
    """Checking FilterEvents. Returns subset of rows"""

    eventsheader = ['patient_id', 'date', 'icd_version', 'icd_code']
    row0 = [['id-123', '2017-02-23', '9', 'V72.0']]

    # The second row is invalid and should be removed

    row1 = [['id-123', '2017-02-23', '9', 'V72.0'],
            ['id-1234', '2017-02-23', '9', '']]
    row2 = [['id-123', '2017-02-23', '9', 'V72.0'],
            ['id-1232', '2015-02-23', '10']]
    row3 = [['id-123', '2017-02-23', '9', 'V72.0'],
            ['id-1234', '2012-22-23', '9', '230.0']]
    row4 = [['id-123', '2017-02-23', '9', 'V72.0'],
            ['id-', '2017-02-23', '9', '230.0']]
    assert FilterEvents(row0, eventsheader) == row0
    assert FilterEvents(row1, eventsheader) == row0
    assert FilterEvents(row2, eventsheader) == row0
    assert FilterEvents(row4, eventsheader) == row0


def test_GetSystem():
    """Checking GetSystem"""

    assert GetSystem('9') == 'http://hl7.org/fhir/sid/icd-9-cm'
    assert GetSystem(9) == 'http://hl7.org/fhir/sid/icd-9-cm'
    assert GetSystem('10') == 'http://hl7.org/fhir/sid/icd-10'
    assert GetSystem(10) == 'http://hl7.org/fhir/sid/icd-10'


def test_GetEvents():
    """Checking GetEvents"""

    eventsheader = ['patient_id', 'date', 'icd_version', 'icd_code']
    row0 = [['id-123', '2017-02-23', '9', 'V72.0']]
    out0 = [{'date': '2017-02-23',
             'system': 'http://hl7.org/fhir/sid/icd-9-cm',
             'code': 'V72.0'}]
    row1 = [['id-123', '2017-02-23', '9', 'Z01.00'],
            ['id-1234', '2017-02-22', '10', '367.0']]
    out1 = [{'date': '2017-02-23', 'code': 'Z01.00',
             'system': 'http://hl7.org/fhir/sid/icd-9-cm'},
            {'date': '2017-02-22', 'code': '367.0',
             'system': 'http://hl7.org/fhir/sid/icd-10'}]

    assert GetEvents(row0, eventsheader) == out0
    assert GetEvents(row1, eventsheader) == out1


def test_GetPatientTimeline():
    """Checking GetPatientTimeline"""

    eventsheader = ['patient_id', 'date', 'icd_version', 'icd_code']
    row = [['id-123', '2017-09-23', '9', 'Z01.00'],
           ['id-123', '2017-08-22', '9', '367.0']]

    assert GetPatientTimeline(row, eventsheader) == 32


def test_GetMedian():
    """Test GetMedian. Sorted row should be input"""

    assert GetMedian([1]) == 1
    assert GetMedian([1, 1]) == 1
    assert GetMedian([1, 1, 2, 4]) == 1.5
    assert GetMedian([0, 2, 5, 6, 8, 9, 9]) == 6
    assert GetMedian([0, 0, 0, 0, 4, 4, 6, 8]) == 2
