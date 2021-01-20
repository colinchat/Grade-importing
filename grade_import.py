import csv
import time

lFile = open('ME 101 - Winter 2021_GradesExport.csv', 'r')
lReader = csv.DictReader(lFile)
lFieldnames = lReader.fieldnames
learn = list(lReader)
lFile.close()

mFile = open('marmoset placeholder 1.csv', 'r')
mReader = csv.DictReader(mFile)
mFieldnames = mReader.fieldnames
marmosetT = list(mReader)
mFile.close()

mFile = open('marmoset placeholder 2.csv', 'r')
mReader = csv.DictReader(mFile)
marmosetW = list(mReader)
mFile.close()

marmoset = marmosetT + marmosetW
# for each row in combined list of marmoset submissions (ALL), search and label previous submissions
for row1 in marmoset:
    time1 = row1["UTC"];
    row2 = row1 # attempting to make more efficient by starting at first iterator in second loop, not sure if this works
    for row2 in marmoset:
        time2 = row2["UTC"]
        if row1["classAccount"] == row2["classAccount"]:
            # if time is different label the duplicates, taking most recent submission
            if time1 < time2:
                row1["classAccount"] = "duplicate";
            elif time1 > time2:
                row2["classAccount"] = "duplicate";

test = open('test4.csv', 'w', newline='')
write = csv.DictWriter(test, mFieldnames)
write.writerows(marmoset)
test.close()

# filter out the duplicates
marmoset = list(filter(lambda d: d["classAccount"] != "duplicate", marmoset))

test = open('test3.csv', 'w', newline='')
write = csv.DictWriter(test, mFieldnames)
write.writerows(marmoset)
test.close()

cFile = open('crowdmark placeholder.csv', 'r')
cReader = csv.DictReader(cFile)
crowdmark = list(cReader)
cFile.close()

eFile = open('Extensions.csv', 'r')
eReader = csv.DictReader(eFile)
extensions = list(eReader)
eFile.close()

# combine marks 
for line in learn:
    student = line["Username"]
    mMark = 1000; 
    cMark = 1000;
    # check both lists
    for row in marmoset:
        if '#' + row["classAccount"] == student:
            mMark = row["total"]
    for row in crowdmark:
        if '#' + row["cvsAccount"] == student: 
            cMark = row["total"] 
    # check that marks were found before recording sum
    if mMark == 1000:
        line["Assignment 1 Points Grade <Numeric MaxPoints:13 Weight:10 Category:Assignments CategoryWeight:15>"] = "MISSING"
        print("missing marmoset info ONLY for " + student)
    elif cMark == 1000:
        line["Assignment 1 Points Grade <Numeric MaxPoints:13 Weight:10 Category:Assignments CategoryWeight:15>"] = "MISSING"
        print("missing crowdmark info ONLY for " + student)
    else:
        line["Assignment 1 Points Grade <Numeric MaxPoints:13 Weight:10 Category:Assignments CategoryWeight:15>"] = float(mMark) + float(cMark)

# write final data to new file
newFile = open('Assignment 1 Learn Import.csv', 'w', newline='')
writer = csv.DictWriter(newFile, lFieldnames)
writer.writeheader()
writer.writerows(learn)
newFile.close()


