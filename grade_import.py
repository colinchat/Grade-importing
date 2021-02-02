# IMPORTANT NOTE:
# don't edit any input files, excel reformats strings of integer dates to scientific

import json
import csv
from datetime import datetime, timedelta, timezone

configFile = open('config.json', 'r')
config = json.load(configFile)
configFile.close()

def listFromCSV(listOfFiles):
    allFiles = list()
    for file in listOfFiles:
        with open(file, newline='') as csvFile:
            reader = csv.DictReader(csvFile)
            allFiles += list(reader)
    return allFiles
    
def getDueDate(student):
    for row in learnData:
        if '#' + student == row[config["header"]["learn_ID"]]:
            return row["temp due date"]
    return "FAILED"

learnData = listFromCSV([config["file"]["learn_format_export"]])
extensions = listFromCSV([config["file"]["extensions"]])
marmosetData = listFromCSV([config["file"]["marmoset_tues"], config["file"]["marmoset_wed"]])
crowdmarkData = listFromCSV([config["file"]["crowdmark_tues"], config["file"]["crowdmark_wed"]])

tuesDate = datetime.strptime(config["dates"]["tues_due_datetime"], '%Y-%m-%d %H:%M:%S %z')
wedDate = datetime.strptime(config["dates"]["wed_due_datetime"], '%Y-%m-%d %H:%M:%S %z')

print("Extensions found:")
# find due dates for all students
for line in learnData:
    extTime = timedelta(hours = 0)
    # check all rows in extensions.csv for each line in learnData
    # (assume extensions.csv is unique to the assignment)
    for row in extensions:
        if '#' + row[config["header"]["ext_ID"]] == line[config["header"]["learn_ID"]]:
            extTime = timedelta(hours = int(config["dates"]["ext_length_in_hours"]))
            print("[SYSTEM]" + row[config["header"]["ext_ID"]] + " was given an extension.")
    # match the lab session to due date, add any extensions if found
    if line[config["header"]["learn_section"]] == "242 Tuesday Lab":
        line["temp due date"] = tuesDate + extTime
    elif line[config["header"]["learn_section"]] == "241 Wednesday Lab":
        line["temp due date"] = wedDate + extTime
    else:
        line["temp due date"] = "ERROR: lab session not found"
# now have list of adjusted due dates appended to learnData doc in last column (after end of line indicator, do not write to import file)

print("\nLate submissions found:")

# calculate adjusted marmosetData grades
for row in marmosetData:
    subDate = datetime.fromtimestamp(int(row[config["header"]["marm_date"]]) / 1000, tz = timezone.utc)
    dueDate = getDueDate(row[config["header"]["marm_ID"]])
    if getDueDate(row[config["header"]["marm_ID"]]) != "FAILED" and subDate > dueDate:
        if subDate - dueDate < timedelta(hours = 24):
            row[config["header"]["marm_grade"]] = round(float(row[config["header"]["marm_grade"]]) * 0.8, 3)
            print("[MARM]Late penalty of 20% applied to " + row[config["header"]["marm_ID"]] + ":\n   submitted on  ", subDate, "\n   with due date ", dueDate)
        elif subDate - dueDate < timedelta(hours = 48):
            row[config["header"]["marm_grade"]] = round(float(row[config["header"]["marm_grade"]]) * 0.6, 3)
            print("[MARM]Late penalty of 40% applied to " + row[config["header"]["marm_ID"]] + ":\n   submitted on  ", subDate, "\n   with due date ", dueDate)
        else:
            row[config["header"]["marm_grade"]] = 0
            print("[MARM]Late penalty of 100% applied to " + row[config["header"]["marm_ID"]] + ":\n   submitted on  ", subDate, "\n   with due date ", dueDate)

# take highest grade from each student
for i in range(len(marmosetData)):
    if marmosetData[i][config["header"]["marm_ID"]] != "to be removed":
        student = marmosetData[i][config["header"]["marm_ID"]]
        highestGrade = float(marmosetData[i][config["header"]["marm_grade"]])
        highestGradeIndex = i
        for j in range(len(marmosetData)):
            row = marmosetData[j]
            if student == row[config["header"]["marm_ID"]]:
                if highestGrade < float(row[config["header"]["marm_grade"]]):
                    highestGrade = float(row[config["header"]["marm_grade"]])
                    highestGradeIndex = j
        for k in range(len(marmosetData)):
            row = marmosetData[k]
            if student == row[config["header"]["marm_ID"]] and highestGradeIndex != k:
                row[config["header"]["marm_ID"]] = "to be removed"
marmosetData = list(filter(lambda d: d[config["header"]["marm_ID"]] != "to be removed", marmosetData))

# calculate adjusted crowdmarkData grades
for row in crowdmarkData:
    student = row[config["header"]["crowd_ID"]].split("@")[0]
    if row[config["header"]["crowd_date"]]:
        subDate = datetime.strptime(row[config["header"]["crowd_date"]], '%Y-%m-%d %H:%M:%S %Z')
        subDate = subDate.replace(tzinfo=timezone.utc)
    else:
        print("[CROWD]Student did not submit: " + row[config["header"]["crowd_ID"]].split("@")[0])
        continue
    dueDate = getDueDate(student)
    if getDueDate(student) != "FAILED" and subDate > dueDate:
        if subDate - dueDate < timedelta(hours = 24):
            row[config["header"]["crowd_grade"]] = round(float(row["Total"]) * 0.8, 3)
            row[config["header"]["crowd_penalty"]] = "20"
            print("[CROWD]Late penalty of 20% applied to " + row["Total"].split("@")[0] + ":\n   submitted on  ", subDate, "\n   with due date ", dueDate)
        elif subDate - dueDate < timedelta(hours = 48):
            row[config["header"]["crowd_grade"]] = round(float(row["Total"]) * 0.6, 3)
            row[config["header"]["crowd_penalty"]] = "40"
            print("[CROWD]Late penalty of 40% applied to " + row[config["header"]["crowd_ID"]].split("@")[0] + ":\n   submitted on  ", subDate, "\n   with due date ", dueDate)
        else:
            row[config["header"]["crowd_grade"]] = 0
            row[config["header"]["crowd_penalty"]] = "100"
            print("[CROWD]Late penalty of 100% applied to " + row[config["header"]["crowd_ID"]].split("@")[0] + ":\n   submitted on  ", subDate, "\n   with due date ", dueDate)
print("\nErrors found: ")

# combine marks from marmosetData and crowdmarkData lists
for line in learnData:
    student = line[config["header"]["learn_ID"]]
    mMark = 1000; 
    cMark = 1000;
    # check both lists
    for row in marmosetData:
        if '#' + row[config["header"]["marm_ID"]] == student:
            mMark = row[config["header"]["marm_grade"]]
    for row in crowdmarkData:
        if '#' + row[config["header"]["crowd_ID"]].split("@")[0] == student and row[config["header"]["crowd_grade"]]: # crowdmarkData leaves blank space if not graded
            cMark = row[config["header"]["crowd_grade"]] 
    # check that marks were found before recording sum
    if mMark == 1000 and cMark == 1000:
        print("[SYSTEM]Missing all info for " + student)
    elif mMark == 1000:
        line[config["header"]["learn_grade"]] = "N/A"
        print("[MARM] missing info for " + student)
    elif cMark == 1000:
        line[config["header"]["learn_grade"]] = "N/A"
        print("[CROWD] missing info for " + student)
    else:
        line[config["header"]["learn_grade"]] = float(mMark) + float(cMark)

# write all data to formatted output file
for line in learnData:
    del line["temp due date"]
with open(config["file"]["output_name"], 'w', newline='') as newFile:
    writer = csv.DictWriter(newFile, learnData[0].keys())
    writer.writeheader()
    writer.writerows(learnData)

# TEST CASE 1
baselineOutput = listFromCSV(["A1_grade_import_BASELINE.csv"])
currOutput = listFromCSV([config["file"]["output_name"]])
if len(baselineOutput) != len(currOutput):
    print("TEST_1 FAILED - different length lists")
else:
    for base, curr in zip(baselineOutput, currOutput):
        if base != curr:
            print("TEST_1 FAILED - line different")
            print("   current is " + curr[config["header"]["learn_ID"]] + " vs " + base[config["header"]["learn_ID"]])
            print("   current is " + curr[config["header"]["learn_grade"]] + " vs " + base[config["header"]["learn_grade"]])

