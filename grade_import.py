# IMPORTANT NOTE: don't edit any input files, excel reformats strings of integer dates to scientific
"""NOTES:
class could be generalized more, to accompany any sort of file with student IDs and information tied to them
    need a way to keep track of and omit certain headers (grade and dates), use class for extension list

need to format student IDs and dates for more clear coding
need to handle blank entries (remove them?)

maybe taking data from the grade exports is better than reformatting the grade exports...

dogfood whole process
    reduce code outside class
    UNIX philosophy
    overall documentation/overview
    python and markdown file
    create extensions file?



"""

import json
import csv
from datetime import datetime, timedelta, timezone

configFile = open('config.json', 'r')
config = json.load(configFile)
configFile.close()


class GradeFile:
    """Container for any files containing student grades"""

    # change parameters to a single list of 4 headers (which will come from config)
    def __init__(self, dict_of_headers, file_name=None):
        if file_name:
            with open(file_name, newline='') as csvFile:
                new_reader = csv.DictReader(csvFile)
                self.data = list(new_reader)
        else:
            self.data = list()
        self.id = dict_of_headers["id"]
        self.grade = dict_of_headers["grade"]
        self.subdate = dict_of_headers["subdate"]
        self.duedate = dict_of_headers["duedate"]

    def combine_with(self, other):
        if type(other) is not GradeFile:
            raise TypeError("Parameter must be type GradeFile")
        elif self.id != other.id:
            raise TypeError("Parameter must have same defined headers")
        elif self.grade != other.grade:
            raise TypeError("Parameter must have same defined headers")
        elif self.subdate != other.subdate:
            raise TypeError("Parameter must have same defined headers")
        elif self.duedate != other.duedate:
            raise TypeError("Parameter must have same defined headers")
        else:
            combined = GradeFile({"id": self.id,
                                  "grade": self.grade,
                                  "subdate": self.subdate,
                                  "duedate": ""})
            combined.data = self.data + other.data
            return combined

    def assign_due_date(self, due_datetime):
        if self.duedate is None:
            self.duedate = 'duedate'
        for row in self.data:
            row[self.duedate] = due_datetime

    def format_duedates_from_string(self, old_format):
        if self.duedate not in self.data[0].keys():
            raise KeyError("Due date column not recognized, review initialization")

        for row in self.data:
            if type(row[self.duedate]) is not str:
                raise TypeError("Date already formatted")
            if row[self.duedate]:
                new_date = datetime.strptime(row[self.duedate], old_format)
                new_date = new_date.replace(tzinfo=timezone.utc)
                row[self.duedate] = new_date

    def format_subdates_from_string(self, old_format):
        if self.subdate not in self.data[0].keys():
            raise KeyError("Due date column not recognized, review initialization")

        for row in self.data:
            if type(row[self.subdate]) is not str:
                raise TypeError("Date already formatted")
            if row[self.subdate]:
                new_date = datetime.strptime(row[self.subdate], old_format)
                new_date = new_date.replace(tzinfo=timezone.utc)
                row[self.subdate] = new_date

    def format_duedates_from_timestamp(self):
        if self.duedate not in self.data[0].keys():
            raise KeyError("Due date column not recognized, review initialization")

        try:
            for row in self.data:
                if type(row[self.duedate]) is not str:
                    raise TypeError("Date already formatted")
                if row[self.duedate]:
                    new_date = datetime.fromtimestamp(int(row[self.duedate]), tz=timezone.utc)
                    row[self.duedate] = new_date
        except OSError:
            for row in self.data:
                if type(row[self.duedate]) is not str:
                    raise TypeError("Date already formatted")
                if row[self.duedate]:
                    new_date = datetime.fromtimestamp(int(row[self.duedate]) / 1000, tz=timezone.utc)
                    row[self.duedate] = new_date

    def format_subdates_from_timestamp(self):
        if self.subdate not in self.data[0].keys():
            raise KeyError("Due date column not recognized, review initialization")

        try:
            for row in self.data:
                if type(row[self.subdate]) is not str:
                    raise TypeError("Date already formatted")
                if row[self.subdate]:
                    new_date = datetime.fromtimestamp(int(row[self.subdate]), tz=timezone.utc)
                    row[self.subdate] = new_date
        except OSError:
            for row in self.data:
                if type(row[self.subdate]) is not str:
                    raise TypeError("Date already formatted")
                if row[self.subdate]:
                    new_date = datetime.fromtimestamp(int(row[self.subdate]) / 1000, tz=timezone.utc)
                    row[self.subdate] = new_date

    def format_id(self, delimiter, index):
        for row in self.data:
            row[self.id] = row[self.id].split(delimiter)[index]

    def conditional_extension(self, condition,
                              except_list_of_dict,
                              extension_hours):
        extension_length = timedelta(hours=int(extension_hours))
        for dRow in self.data:
            for eRow in except_list_of_dict:
                if condition(dRow, eRow):
                    new_date = dRow[self.duedate] + extension_length
                    dRow[self.duedate] = new_date

    def conditional_new_due_date(self, condition,
                                 except_list_of_dict,
                                 new_due_date_header,
                                 date_format):
        for dRow in self.data:
            for eRow in except_list_of_dict:
                if condition(dRow, eRow):
                    new_date = datetime.strptime(eRow[new_due_date_header], date_format)
                    if new_date.tzinfo is None or new_date.utcoffset() is None:
                        new_date = new_date.astimezone(timezone.utc)
                    dRow[self.duedate] = new_date
                    print("extension given to " + dRow[self.id])

    def apply_late_penalty(self, multiplier,
                           min_hours_late=0,
                           max_hours_late=1000):
        for row in self.data:
            if row[self.subdate]:
                delta = row[self.subdate] - row[self.duedate]
                if timedelta(hours=min_hours_late) < delta <= timedelta(hours=max_hours_late):
                    print("penalty applied to " + row[self.id])
                    print(delta)
                    print(row[self.subdate])
                    print(row[self.duedate])
                    print(str(row[self.grade]) + '*' + str(multiplier) + '=' + str(
                        float(row[self.grade]) * multiplier) + '\n')
                    row[self.grade] = float(row[self.grade]) * multiplier
                else:
                    row[self.grade] = float(row[self.grade])

    def take_highest_grade(self):
        for row in self.data:
            if row[self.id] != 'remove_flag':
                student_id = row[self.id]
                high_index = 0
                high_grade = 0
                all_index = list()
                for count in range(len(self.data)):
                    if self.data[count][self.id] == student_id:
                        all_index.append(count)
                        if float(self.data[count][self.grade]) >= high_grade:
                            high_index = count
                            high_grade = float(self.data[count][self.grade])
                for num in all_index:
                    if num != high_index:
                        self.data[num][self.id] = 'remove_flag'
        self.data = list(filter(lambda line: line[self.id] != 'remove_flag', self.data))

    def add_to_grade_import(self, other_grade_file):
        for row_self in self.data:
            for row_dest in other_grade_file.data:
                if '#' + row_self[self.id] in row_dest[other_grade_file.id] \
                        or row_dest[other_grade_file.id] in '#' + row_self[self.id]:
                    if row_self[self.grade]:
                        if row_dest[other_grade_file.grade]:
                            row_dest[other_grade_file.grade] = float(row_dest[other_grade_file.grade]) \
                                                               + float(row_self[self.grade])
                        else:
                            row_dest[other_grade_file.grade] = float(row_self[self.grade])


marmTues = GradeFile(config["marm"], config["file"]["marmoset_tues"])
marmWedn = GradeFile(config["marm"], config["file"]["marmoset_wed"])
crowdTue = GradeFile(config["crowd"], config["file"]["crowdmark_tues"])
crowdWed = GradeFile(config["crowd"], config["file"]["crowdmark_wed"])
learnExp = GradeFile(config["learn"], config["file"]["learn_format_export"])

with open(config["file"]["extensions"]) as extFile:
    reader = csv.DictReader(extFile)
    extData = list(reader)

tuesDate = datetime.strptime(config["dates"]["tues_due_datetime"], '%Y-%m-%d %H:%M:%S %z')
wednDate = datetime.strptime(config["dates"]["wed_due_datetime"], '%Y-%m-%d %H:%M:%S %z')

print("Marmoset: ")
marmData = marmTues.combine_with(marmWedn)
marmData.format_subdates_from_timestamp()
marmData.assign_due_date(tuesDate)
marmData.conditional_extension(lambda m, e: "#" + m["classAccount"] == e["Username"] and e[
    "ME101_chulls_pmteerts_1211_LAB"] == "241 Wednesday Lab", learnExp.data, 24)
marmData.conditional_new_due_date(lambda m, e: m[marmData.id] == e["User ID"], extData, '+72 hours', '%Y-%m-%d %H:%M')
marmData.apply_late_penalty(0.8, 0, 24)
marmData.apply_late_penalty(0.6, 24, 48)
marmData.apply_late_penalty(0, 48)
marmData.take_highest_grade()
marmData.add_to_grade_import(learnExp)

print("Crowdmark: ")
crowdTue.format_subdates_from_string('%Y-%m-%d %H:%M:%S %Z')
crowdTue.format_id('@', 0)
crowdTue.assign_due_date(tuesDate)
crowdTue.conditional_new_due_date(lambda m, e: m[crowdTue.id] == e["User ID"], extData, '+72 hours',
                               '%Y-%m-%d %H:%M')
crowdTue.apply_late_penalty(0.8, 0, 24)
crowdTue.apply_late_penalty(0.6, 24, 48)
crowdTue.apply_late_penalty(0, 48)
crowdTue.add_to_grade_import(learnExp)

crowdWed.format_subdates_from_string('%Y-%m-%d %H:%M:%S %Z')
crowdWed.format_id('@', 0)
crowdWed.assign_due_date(wednDate)
crowdWed.conditional_new_due_date(lambda m, e: m[crowdWed.id] == e["User ID"], extData, '+72 hours',
                               '%Y-%m-%d %H:%M')
crowdWed.apply_late_penalty(0.8, 0, 24)
crowdWed.apply_late_penalty(0.6, 24, 48)
crowdWed.apply_late_penalty(0, 48)
crowdWed.add_to_grade_import(learnExp)

with open(config["file"]["output_name"], 'w', newline='') as newFile:
    writer = csv.DictWriter(newFile, learnExp.data[0].keys())
    writer.writeheader()
    writer.writerows(learnExp.data)


def list_from_csv(list_of_files):
    all_files = list()
    for file in list_of_files:
        with open(file, newline='') as csvFile:
            new_reader = csv.DictReader(csvFile)
            all_files += list(new_reader)
    return all_files


# TEST CASE 1
baseline = list_from_csv(["A1_grade_import_BASELINE.csv"])
current = list_from_csv([config["file"]["output_name"]])
if len(baseline) != len(current):
    print("TEST_1 FAILED - different length lists")
else:
    for base, curr in zip(baseline, current):
        if base != curr:
            print("TEST_1 FAILED - line different")
            print("   current is " + curr[config["learn"]["id"]] + " vs " + base[config["learn"]["id"]])
            print("   current is " + curr[config["learn"]["grade"]] + " vs " + base[config["learn"]["grade"]])
