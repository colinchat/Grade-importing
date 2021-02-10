# IMPORTANT NOTE: don't edit any input files, excel reformats strings of integer dates to scientific
"""NOTES:
class could be generalized more, to accompany any sort of file with student IDs and information tied to them
    need a way to keep track of and omit certain headers (grade and dates), use class for extension list

need to format student IDs and dates for more clear coding
need to handle blank entries (remove them?)

maybe taking data from the grade exports is better than reformatting the grade exports...
"""
import json
import csv
from datetime import datetime, timedelta, timezone

configFile = open('config.json', 'r')
config = json.load(configFile)
configFile.close()

class gradeFile:
    """Container for any files containing student grades"""
    def __init__(self, ID_header_string, grade_header_string, date_header_string, file_name = None):
        if file_name:
            with open(file_name, newline='') as csvFile:
                reader = csv.DictReader(csvFile)
                self.data = list(reader)
        else:
            self.data = list()
        self.strID = ID_header_string
        self.strGrade = grade_header_string
        self.strSubDate = date_header_string

    def __add__(self, other):
        if self.strID == other.strID and self.strGrade == other.strGrade and self.strSubDate == other.strSubDate:
            temp = gradeFile(self.strID, self.strGrade, self.strSubDate)
            temp.data = self.data + other.data
            return temp
        else:
            return bool(false) # error/exception implementation?

    def formatSubDates(self, old_strp_format = None):
        if old_strp_format == None:
            try:
                for row in self.data:
                    temp = datetime.fromtimestamp(int(row[self.strSubDate]) / 1000, tz = timezone.utc)
                    row[self.strSubDate] = temp
            except OSError:
                for row in self.data:
                    temp = datetime.fromtimestamp(int(row[self.strSubDate]), tz = timezone.utc)
                    row[self.strSubDate] = temp
        else:
            for row in self.data:
                if row[self.strSubDate]:
                    temp = datetime.strptime(row[self.strSubDate], old_strp_format)
                    temp = temp.replace(tzinfo=timezone.utc)
                    row[self.strSubDate] = temp
        
    def assignDueDate(self, due_date):
        for row in self.data:
            row['dueDate'] = due_date
    
    def conditionalExtension(self, condition, except_list_of_dict, extension_hours):
        extensionLength = timedelta(hours = int(extension_hours))
        for dRow in self.data:
            for eRow in except_list_of_dict:
                if condition(dRow, eRow):
                    newDate = dRow['dueDate'] + extensionLength
                    dRow['dueDate'] = newDate

    def conditionalNewDueDate(self, condition, except_list_of_dict, new_due_date_header, date_format):
        for dRow in self.data:
            for eRow in except_list_of_dict:
                if condition(dRow, eRow):
                    # timezone picked base on system timezone since importing naive date, should explicitly define it instead
                    newDate = datetime.strptime(eRow[new_due_date_header], date_format)
                    newDate = newDate.astimezone(timezone.utc)
                    dRow['dueDate'] = newDate
    
    def applyLatePenalty(self, multiplier, min_hours_late = 0, max_hours_late = 1000):
        for row in self.data:
            if row[self.strSubDate]:
                delta = row[self.strSubDate] - row['dueDate']
                if delta > timedelta(hours = min_hours_late) and delta <= timedelta(hours = max_hours_late):
                    row[self.strGrade] = float(row[self.strGrade]) * multiplier
                    print("penalty applied to " + row[self.strID])
                    print(str(row[self.strGrade]) + '*' + str(multiplier) + '=' + str(row[self.strGrade]) + '\n')
                else:
                    row[self.strGrade] = float(row[self.strGrade])
        
    def takeHighestNewGrade(self):
        for row in self.data:
            if row[self.strID] != 'remove_flag':
                studentID = row[self.strID]
                highIndex = 0
                highGrade = 0
                allIndex = list()
                for count in range(len(self.data)):
                    if self.data[count][self.strID] == studentID:
                        allIndex.append(count)
                        if float(self.data[count][self.strGrade]) >=  highGrade:
                            highIndex = count
                            highGrade = float(self.data[count][self.strGrade])
                for num in allIndex:
                    if num != highIndex:
                        self.data[num][self.strID] = 'remove_flag'
        self.data = list(filter(lambda row: row[self.strID] != 'remove_flag', self.data))

    def addToGradeImport(self, other_grade_file):
        for row_self in self.data:
            for row_dest in other_grade_file.data:
                if '#' + row_self[self.strID] in row_dest[other_grade_file.strID] or row_dest[other_grade_file.strID] in '#' + row_self[self.strID]:
                    if row_self[self.strGrade]:
                        if row_dest[other_grade_file.strGrade]:
                            row_dest[other_grade_file.strGrade] = float(row_dest[other_grade_file.strGrade]) + float(row_self[self.strGrade])
                        else:
                            row_dest[other_grade_file.strGrade] = float(row_self[self.strGrade])

marmTues = gradeFile(config["header"]["marm_ID"], config["header"]["marm_grade"], config["header"]["marm_date"], config["file"]["marmoset_tues"])
marmWedn = gradeFile(config["header"]["marm_ID"], config["header"]["marm_grade"], config["header"]["marm_date"], config["file"]["marmoset_wed"])
crowdTue = gradeFile(config["header"]["crowd_ID"], config["header"]["crowd_grade"], config["header"]["crowd_date"], config["file"]["crowdmark_tues"])
crowdWed = gradeFile(config["header"]["crowd_ID"], config["header"]["crowd_grade"], config["header"]["crowd_date"], config["file"]["crowdmark_wed"])
learnExp = gradeFile(config["header"]["learn_ID"], config["header"]["learn_grade"], 'N/A', config["file"]["learn_format_export"])
with open(config["file"]["extensions"]) as extFile:
    reader = csv.DictReader(extFile)
    extData = list(reader)

tuesDate = datetime.strptime(config["dates"]["tues_due_datetime"], '%Y-%m-%d %H:%M:%S %z')
wednDate = datetime.strptime(config["dates"]["wed_due_datetime"], '%Y-%m-%d %H:%M:%S %z')

marmData = marmTues + marmWedn
marmData.formatSubDates()
marmData.assignDueDate(tuesDate)
marmData.conditionalExtension(lambda m, e: "#" + m["classAccount"] == e["Username"] and e["ME101_chulls_pmteerts_1211_LAB"] == "241 Wednesday Lab", learnExp.data, 24)
marmData.conditionalNewDueDate(lambda m, e: m[marmData.strID] == e["User ID"], extData, '+72 hours', '%Y-%m-%d %H:%M')
marmData.applyLatePenalty(0.8, 0, 24)
marmData.applyLatePenalty(0.6, 24, 48)
marmData.applyLatePenalty(0, 48)
marmData.takeHighestNewGrade()
marmData.addToGradeImport(learnExp)

crowdTue.formatSubDates('%Y-%m-%d %H:%M:%S %Z')
crowdTue.assignDueDate(tuesDate)
crowdTue.applyLatePenalty(0.8, 0, 24)
crowdTue.applyLatePenalty(0.6, 24, 48)
crowdTue.applyLatePenalty(0, 48)
crowdTue.addToGradeImport(learnExp)

crowdWed.formatSubDates('%Y-%m-%d %H:%M:%S %Z')
crowdWed.assignDueDate(wednDate)
crowdWed.applyLatePenalty(0.8, 0, 24)
crowdWed.applyLatePenalty(0.6, 24, 48)
crowdWed.applyLatePenalty(0, 48)
crowdWed.addToGradeImport(learnExp)

with open(config["file"]["output_name"], 'w', newline='') as newFile:
    writer = csv.DictWriter(newFile, learnExp.data[0].keys())
    writer.writeheader()
    writer.writerows(learnExp.data)

def listFromCSV(listOfFiles):
    allFiles = list()
    for file in listOfFiles:
        with open(file, newline='') as csvFile:
            reader = csv.DictReader(csvFile)
            allFiles += list(reader)
    return allFiles

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

