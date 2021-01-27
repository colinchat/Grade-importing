import json
import csv
from datetime import datetime, timedelta, timezone

configFile = open('config.json', 'r')
configData = json.load(configFile)
configFile.close()

# learnData export template
lFile = open(configData["file"]["learn_format_export"], 'r')
lReader = csv.DictReader(lFile)
lFieldnames = lReader.fieldnames
learnData = list(lReader)
lFile.close()

# extensions file import (single sheet unique to assignment)
eFile = open(configData["file"]["extensions"], 'r')
eReader = csv.DictReader(eFile)
extensions = list(eReader)
eFile.close()

# original due dates for each lab section
tuesDate = datetime.strptime(configData["dates"]["tues_due_datetime"], '%Y-%m-%d %H:%M:%S %z')
wedDate = datetime.strptime(configData["dates"]["wed_due_datetime"], '%Y-%m-%d %H:%M:%S %z')

print("Extensions found:")
for line in learnData:
    extTime = timedelta(hours = 0)
    # check all rows in extensions.csv for each line in learnData
    # (assume extensions.csv is unique to the assignment)
    for row in extensions:
        if '#' + row["User ID"] == line["Username"]:
            extTime = timedelta(hours = int(configData["dates"]["ext_length_in_hours"]))
            print("[SYSTEM]" + row["User ID"] + " was given an extension.")
    # match the lab session to due date, add any extensions if found
    if line["ME101_chulls_pmteerts_1211_LAB"] == "242 Tuesday Lab":
        line["due date UTC"] = tuesDate + extTime
    elif line["ME101_chulls_pmteerts_1211_LAB"] == "241 Wednesday Lab":
        line["due date UTC"] = wedDate + extTime
    else:
        line["due date UTC"] = "ERROR: lab session not found"
# now have list of adjusted due dates appended to learnData doc in last column (after end of line indicator, do not write to import file)

# marmosetData file import
mFile1 = open(configData["file"]["marmoset_tues"], 'r')
mReader1 = csv.DictReader(mFile1)
mFieldnames = mReader1.fieldnames
marmosetDataT = list(mReader1)
mFile1.close()
mFile2 = open(configData["file"]["marmoset_wed"], 'r')
mReader2 = csv.DictReader(mFile2)
marmosetDataW = list(mReader2)
mFile2.close()

marmosetData = marmosetDataT + marmosetDataW

def getDueDate(student):
    for row in learnData:
        if '#' + student == row["Username"]:
            return row["due date UTC"]
    return "FAILED"
print("\nLate submissions found:")

newFile = open('test.csv', 'w', newline='')
writer = csv.DictWriter(newFile, mFieldnames)
writer.writeheader()
writer.writerows(marmosetData)
newFile.close()

# calculate adjusted marmosetData grades
for row in marmosetData:
    subDate = datetime.fromtimestamp(int(row["UTC"]) / 1000, tz = timezone.utc)
    dueDate = getDueDate(row["classAccount"])
    if getDueDate(row["classAccount"]) != "FAILED" and subDate > dueDate:
        if subDate - dueDate < timedelta(hours = 24):
            row["total"] = round(float(row["total"]) * 0.8, 3)
            print("[MARM]Late penalty of 20% applied to " + row["classAccount"] + ":\n   submitted on  ", subDate, "\n   with due date ", dueDate)
        elif subDate - dueDate < timedelta(hours = 48):
            row["total"] = round(float(row["total"]) * 0.6, 3)
            print("[MARM]Late penalty of 40% applied to " + row["classAccount"] + ":\n   submitted on  ", subDate, "\n   with due date ", dueDate)
        else:
            row["total"] = 0
            print("[MARM]Late penalty of 100% applied to " + row["classAccount"] + ":\n   submitted on  ", subDate, "\n   with due date ", dueDate)

# take highest grade from each student
for i in range(len(marmosetData)):
    if marmosetData[i]["classAccount"] != "to be removed":
        student = marmosetData[i]["classAccount"]
        highestGrade = float(marmosetData[i]["total"])
        highestGradeIndex = i
        for j in range(len(marmosetData)):
            row = marmosetData[j]
            if student == row["classAccount"]:
                if highestGrade < float(row["total"]):
                    highestGrade = float(row["total"])
                    highestGradeIndex = j
        for k in range(len(marmosetData)):
            row = marmosetData[k]
            if student == row["classAccount"] and highestGradeIndex != k:
                row["classAccount"] = "to be removed"
marmosetData = list(filter(lambda d: d["classAccount"] != "to be removed", marmosetData))

# crowdmarkData file import
cFile1 = open(configData["file"]["crowdmark_tues"], 'r')
cReader1 = csv.DictReader(cFile1)
cFieldnames = cReader1.fieldnames
crowdmarkDataT = list(cReader1)
cFile1.close()
cFile2 = open(configData["file"]["crowdmark_wed"], 'r')
cReader2 = csv.DictReader(cFile2)
crowdmarkDataW = list(cReader2)
cFile2.close()

crowdmarkData = crowdmarkDataT + crowdmarkDataW

# calculate adjusted crowdmarkData grades
for row in crowdmarkData:
    student = row["Email"].split("@")[0]
    if row["Submitted At"]:
        subDate = datetime.strptime(row["Submitted At"], '%Y-%m-%d %H:%M:%S %Z')
        subDate = subDate.replace(tzinfo=timezone.utc)
    else:
        print("[CROWD]Student did not submit: " + row["Email"].split("@")[0])
        continue
    dueDate = getDueDate(student)
    if getDueDate(student) != "FAILED" and subDate > dueDate:
        if subDate - dueDate < timedelta(hours = 24):
            row["Total After Penalty"] = round(float(row["Total"]) * 0.8, 3)
            row["Custom Penalty"] = "20"
            print("[CROWD]Late penalty of 20% applied to " + row["Email"].split("@")[0] + ":\n   submitted on  ", subDate, "\n   with due date ", dueDate)
        elif subDate - dueDate < timedelta(hours = 48):
            row["Total After Penalty"] = round(float(row["Total"]) * 0.6, 3)
            row["Custom Penalty"] = "40"
            print("[CROWD]Late penalty of 40% applied to " + row["Email"].split("@")[0] + ":\n   submitted on  ", subDate, "\n   with due date ", dueDate)
        else:
            row["Total After Penalty"] = 0
            row["Custom Penalty"] = "100"
            print("[CROWD]Late penalty of 100% applied to " + row["Email"].split("@")[0] + ":\n   submitted on  ", subDate, "\n   with due date ", dueDate)
print("\nErrors found: ")

# combine marks from marmosetData and crowdmarkData lists
for line in learnData:
    student = line["Username"]
    mMark = 1000; 
    cMark = 1000;
    # check both lists
    for row in marmosetData:
        if '#' + row["classAccount"] == student:
            mMark = row["total"]
    for row in crowdmarkData:
        if '#' + row["Email"].split("@")[0] == student and row["Total After Penalty"]: # crowdmarkData leaves blank space if not graded
            cMark = row["Total After Penalty"] 
    # check that marks were found before recording sum
    if mMark == 1000 and cMark == 1000:
        print("[SYSTEM]Missing all info for " + student)
    elif mMark == 1000:
        line["Assignment 1 Points Grade <Numeric MaxPoints:13 Weight:10 Category:Assignments CategoryWeight:10>"] = "N/A"
        print("[MARM] missing info for " + student)
    elif cMark == 1000:
        line["Assignment 1 Points Grade <Numeric MaxPoints:13 Weight:10 Category:Assignments CategoryWeight:10>"] = "N/A"
        print("[CROWD] missing info for " + student)
    else:
        line["Assignment 1 Points Grade <Numeric MaxPoints:13 Weight:10 Category:Assignments CategoryWeight:10>"] = float(mMark) + float(cMark)

# write final data to new file
newFile = open(configData["file"]["output_name"], 'w', newline='')
writer = csv.DictWriter(newFile, lFieldnames)
writer.writeheader()
for line in learnData:
    del line["due date UTC"]
    writer.writerow(line)
newFile.close()

# other compiled lists written to excel for debugging
newFile = open('marmosetData_compiled.csv', 'w', newline='')
writer = csv.DictWriter(newFile, mFieldnames)
writer.writeheader()
writer.writerows(marmosetData)
newFile.close()

newFile = open('crowdmarkData_compiled.csv', 'w', newline='')
writer = csv.DictWriter(newFile, cFieldnames)
writer.writeheader()
writer.writerows(crowdmarkData)
newFile.close()

newFile = open('learnData_compiled.csv', 'w', newline='')
writer = csv.DictWriter(newFile, lFieldnames)
writer.writeheader()
writer.writerows(learnData)
newFile.close()

