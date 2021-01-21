import csv
from datetime import datetime, timedelta, timezone

# learn export template
lFile = open('ME 101 - Winter 2021_GradesExport.csv', 'r')
lReader = csv.DictReader(lFile)
lFieldnames = lReader.fieldnames
lFieldnames.append("due date UTC")
learn = list(lReader)
lFile.close()

# extensions file import (single sheet unique to assignment)
eFile = open('Extensions.csv', 'r')
eReader = csv.DictReader(eFile)
extensions = list(eReader)
eFile.close()

# --------------original due dates (change these each assignment)---------------------
tuesDate = datetime.strptime("2021-1-13 21:30:59 +0000", '%Y-%m-%d %H:%M:%S %z')
wedDate = datetime.strptime("2021-1-14 21:30:59 +0000", '%Y-%m-%d %H:%M:%S %z')
# ------------------------------------------------------------------------------------

print("Extensions found:")
for line in learn:
    extTime = timedelta(hours = 0)
    # check all rows in extensions.csv for each line in learn
    # (assume extensions.csv is unique to the assignment)
    for row in extensions:
        if '#' + row["User ID"] == line["Username"]:
            extTime = timedelta(hours = 72)
            print("[SYSTEM]" + row["User ID"] + " was given an extension.")
    # match the lab session to due date, add any extensions if found
    if line["ME101_chulls_pmteerts_1211_LAB"] == "242 Tuesday Lab":
        line["due date UTC"] = tuesDate + extTime
    elif line["ME101_chulls_pmteerts_1211_LAB"] == "241 Wednesday Lab":
        line["due date UTC"] = wedDate + extTime
    else:
        line["due date UTC"] = "ERROR: lab session not found"
# now have list of adjusted due dates appended to learn doc in last column (after end of line indicator, so OK to import?)

# marmoset file import
mFile1 = open('project-Assignment 1 - Tuesday lab-grades.csv', 'r')
mReader1 = csv.DictReader(mFile1)
mFieldnames = mReader1.fieldnames
marmosetT = list(mReader1)
mFile1.close()
mFile2 = open('project-Assignment 1 - Wednesday lab-grades.csv', 'r')
mReader2 = csv.DictReader(mFile2)
marmosetW = list(mReader2)
mFile2.close()

marmoset = marmosetT + marmosetW

def getDueDate(student):
    for row in learn:
        if '#' + student == row["Username"]:
            return row["due date UTC"]
    return "FAILED"
print("\nLate submissions found:")

newFile = open('test.csv', 'w', newline='')
writer = csv.DictWriter(newFile, mFieldnames)
writer.writeheader()
writer.writerows(marmoset)
newFile.close()

# calculate adjusted marmoset grades
for row in marmoset:
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
for row1 in marmoset:
    student = row1["classAccount"]
    highestGrade = float(row1["total"])
    bestSubDate = datetime.fromtimestamp(int(row1["UTC"]) / 1000, tz = timezone.utc)
    for row2 in marmoset:
        if student == row2["classAccount"]:
            row2["classAccount"] = "to be removed";
            if highestGrade < float(row2["total"]):
                highestGrade = float(row2["total"])
                bestSubDate = datetime.fromtimestamp(int(row2["UTC"]) / 1000, tz = timezone.utc)
    row1["classAccount"] = student
    row1["total"] = highestGrade
    row1["UTC"] = (bestSubDate - datetime(1970, 1, 1, tzinfo = timezone.utc)) / timedelta(seconds=1)
marmoset = list(filter(lambda d: d["classAccount"] != "to be removed", marmoset))

# crowdmark file import
cFile1 = open('a1_prog_tue_lab-marks.csv', 'r')
cReader1 = csv.DictReader(cFile1)
cFieldnames = cReader1.fieldnames
crowdmarkT = list(cReader1)
cFile1.close()
cFile2 = open('a1_prog_wed_lab-marks.csv', 'r')
cReader2 = csv.DictReader(cFile2)
crowdmarkW = list(cReader2)
cFile2.close()

crowdmark = crowdmarkT + crowdmarkW

# calculate adjusted crowdmark grades
for row in crowdmark:
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

# combine marks from marmoset and crowdmark lists
for line in learn:
    student = line["Username"]
    mMark = 1000; 
    cMark = 1000;
    # check both lists
    for row in marmoset:
        if '#' + row["classAccount"] == student:
            mMark = row["total"]
    for row in crowdmark:
        if '#' + row["Email"].split("@")[0] == student and row["Total After Penalty"]: # crowdmark leaves blank space if not graded
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
newFile = open('grade_import.csv', 'w', newline='')
writer = csv.DictWriter(newFile, lFieldnames)
writer.writeheader()
writer.writerows(learn)
newFile.close()

# other compiled lists written to excel for debugging
newFile = open('marmoset_compiled.csv', 'w', newline='')
writer = csv.DictWriter(newFile, mFieldnames)
writer.writeheader()
writer.writerows(marmoset)
newFile.close()

newFile = open('crowdmark_compiled.csv', 'w', newline='')
writer = csv.DictWriter(newFile, cFieldnames)
writer.writeheader()
writer.writerows(crowdmark)
newFile.close()

newFile = open('learn_compiled.csv', 'w', newline='')
writer = csv.DictWriter(newFile, lFieldnames)
writer.writeheader()
writer.writerows(learn)
newFile.close()

