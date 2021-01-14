import csv
import time

mFile = open('marmoset placeholder.csv', 'r')
mReader = csv.DictReader(mFile)
marmoset = list(mReader)
mFile.close()

cFile = open('crowdmark placeholder.csv', 'r')
cReader = csv.DictReader(cFile)
crowdmark = list(cReader)
cFile.close()

lFile = open('ME 101 - Winter 2021_GradesExport.csv', 'r')
lReader = csv.DictReader(lFile)
lFieldnames = lReader.fieldnames
learn = list(lReader)
lFile.close()

eFile = open('Extensions.csv', 'r')
eReader = csv.DictReader(eFile)
extensions = list(eReader)
eFile.close()

# Q FOR DAVID: how to handle two submissions? delete the students who submitted on the other day or combine?
# --> We probably need to keep seperate for due date & late calculation...
#   --> my remove functionality is not working at the moment though

for line in learn:
    student = line["Username"]
    
    mMark = 1000; # initialize to 1000 to avoid accidentally giving student 0
    cMark = 1000;
        
    for row in marmoset:
        if '#' + row["cvsAccount"] == student:
            mMark = row["total"]
    
    for row in crowdmark:
        if '#' + row["cvsAccount"] == student: # PLACEHOLDER NAMES UNTIL CROWDMARK FORMAT AVAILABLE
            cMark = row["total"] 

    if mMark == 1000 and cMark == 1000:
        learn.remove(line) # DOESNT WORK
    elif mMark == 1000:
        print("missing marmoset info ONLY for " + student)
    elif cMark == 1000:
        print("missing crowdmark info ONLY for " + student)
    else:
        line["Assignment 1 Points Grade <Numeric MaxPoints:13 Weight:10 Category:Assignments CategoryWeight:15>"] = float(mMark) + float(cMark)


# new file or just use old learn file?
newFile = open('Assignment 1 Learn Import.csv', 'w', newline='')
writer = csv.DictWriter(newFile, lFieldnames)
writer.writeheader()
writer.writerows(learn)
newFile.close()



# features to implement:
    # need to check marmoset and crowdmark for lateness, then check extensions csv and apply penalty if needed
    # (and print message so grader can manually check before penalties are finalized)

