# Solution to Longitudinal Patient Data Interview Question

## How to run?
To run the program that does the join and gets the required statistics.
```
python main.py -demo ./demo.psv  -events ./events.psv
```

The ouput directory is `./out` (which contains all <patient_id>.json). For more
options use
```
python main.py --help
```

## Unit Testing
I use pytest for testing (may need to be installed). All the tests are in
`tests/test_sample.py`
To run the tests:
```
pytest
```

## Directory Structure and it's important files
These important files are 
* `DemoEventsJoin/app.py` : These contains all the functions. Most functions have unit tests associated with them (except I/O functions)
* `tests/test_sample.py` : Contains are the tests.
* `main.py` : Does the join and measures required statistics.
* `./out` : Contains seperate JSON with each json have filename <patient_id>.json
```
.
├── DemoEventsJoin
│  ├── app.py
├── README.md
├── demo.psv
├── events.psv
├── main.py
├── out
│   ├── id-1011.json
│   ├── id-1019.json
│   ├── ............
├── requirements.txt
└── tests
    └── test_sample.py
```

## Measured Statistics
```
Total number of valid patients is 352
Length of patient timeline: Maximum = 984
Length of patient timeline: Minimun = 0
Length of patient timeline: Median = 0.000000 
(This is because most patients have single 
valid visits which are counted as zero days)
Count of males is 162 and females is 190
Length of patient age: Maximum = 33620
Length of patient age: Minimun = 750
Length of patient age: Median = 22933.000000
```
