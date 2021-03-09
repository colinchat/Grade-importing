import csv


def areequal(file_baseline, file_to_test):
    with open(file_baseline, newline='') as csvFile:
        new_reader = csv.DictReader(csvFile)
        baseline = list(new_reader)

    with open(file_to_test, newline='') as csvFile:
        new_reader = csv.DictReader(csvFile)
        current = list(new_reader)

    if len(baseline) != len(current):
        print("EQUALITY TEST FAILED - different length lists")
    else:
        for base, curr in zip(baseline, current):
            if base != curr:
                print("EQUALITY TEST FAILED - data different")
