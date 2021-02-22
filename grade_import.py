# IMPORTANT NOTE: don't edit any input files, excel reformats strings of integer dates to scientific
"""NOTES:
dogfood whole process
    reduce code outside class
    UNIX philosophy
    overall documentation/overview
    python and markdown file
    document external files (extensions/learn)
"""

import json
import csv
from datetime import datetime, timedelta, timezone

configFile = open('config.json', 'r')
config = json.load(configFile)
configFile.close()


class GradeFile:
    """Container for any files of student grades"""

    def __init__(self, dict_of_headers, file_name=None):
        if file_name is not None:
            with open(file_name, newline='') as inputcsv:
                reader = csv.DictReader(inputcsv)
                self.data = list(reader)
        else:
            self.data = list()

        self.id = dict_of_headers["id"]
        self.grade = dict_of_headers["grade"]
        self.subdate = dict_of_headers["subdate"]
        self.duedate = dict_of_headers["duedate"]

        if self.data:
            if self.id is None:
                raise KeyError("must include id column")

            if self.id is not None and self.id not in self.data[0].keys():
                raise KeyError("id column not found")

            if self.grade is not None and self.grade not in self.data[0].keys():
                raise KeyError("gradecolumn not found")

            if self.subdate is not None and self.subdate not in self.data[0].keys():
                raise KeyError("subdate column not found")

            if self.duedate is not None and self.duedate not in self.data[0].keys():
                raise KeyError("duedate column not found")
        self.duedateformatted = False
        self.subdateformatted = False

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
        elif self.duedateformatted != other.duedateformatted:
            raise TypeError("Inconsistent duedate formatting")
        elif self.subdateformatted != other.subdateformatted:
            raise TypeError("inconsistent subdate formatting")
        else:
            combined = GradeFile({"id": self.id,
                                  "grade": self.grade,
                                  "subdate": self.subdate,
                                  "duedate": self.duedate})
            combined.data = self.data + other.data
            combined.duedateformatted = self.duedateformatted
            combined.subdateformatted = self.subdateformatted
            return combined

    def assign_due_date(self, due_datetime):
        if self.duedate is None:
            self.duedate = 'duedate'
        for row in self.data:
            row[self.duedate] = due_datetime
        self.duedateformatted = True

    def format_duedates_from_string(self, old_format):
        if self.duedateformatted:
            raise TypeError("already formatted due dates")

        if self.duedate is None or self.duedate not in self.data[0].keys():
            raise KeyError("Due date column not recognized, review initialization")

        for row in self.data:
            if type(row[self.duedate]) is not str:
                raise TypeError("Date already formatted")
            if row[self.duedate]:
                new_date = datetime.strptime(row[self.duedate], old_format)
                new_date = new_date.replace(tzinfo=timezone.utc)
                row[self.duedate] = new_date
        self.duedateformatted = True

    def format_subdates_from_string(self, old_format):
        if self.subdateformatted:
            raise TypeError("already formatted sub dates")

        if self.subdate is None or self.subdate not in self.data[0].keys():
            raise KeyError("Due date column not recognized, review initialization")

        for row in self.data:
            if type(row[self.subdate]) is not str:
                raise TypeError("Date already formatted")
            if row[self.subdate]:
                new_date = datetime.strptime(row[self.subdate], old_format)
                new_date = new_date.replace(tzinfo=timezone.utc)
                row[self.subdate] = new_date
        self.subdateformatted = True

    def format_duedates_from_timestamp(self):
        if self.duedateformatted:
            raise TypeError("already formatted due dates")

        if self.duedate is None or self.duedate not in self.data[0].keys():
            raise KeyError("Due date column not recognized, review initialization")

        try:
            for row in self.data:
                if type(row[self.duedate]) is not str:
                    raise TypeError("Date already formatted")
                if row[self.duedate]:
                    new_date = datetime.fromtimestamp(int(row[self.duedate]),
                                                      tz=timezone.utc)
                    row[self.duedate] = new_date
        except OSError:
            for row in self.data:
                if type(row[self.duedate]) is not str:
                    raise TypeError("Date already formatted")
                if row[self.duedate]:
                    new_date = datetime.fromtimestamp(int(row[self.duedate]) / 1000,
                                                      tz=timezone.utc)
                    row[self.duedate] = new_date
        self.duedateformatted = True

    def format_subdates_from_timestamp(self):
        if self.subdateformatted:
            raise TypeError("already formatted sub dates")

        if self.subdate is None or self.subdate not in self.data[0].keys():
            raise KeyError("Due date column not recognized, review initialization")

        try:
            for row in self.data:
                if type(row[self.subdate]) is not str:
                    raise TypeError("Date already formatted")
                if row[self.subdate]:
                    new_date = datetime.fromtimestamp(int(row[self.subdate]),
                                                      tz=timezone.utc)
                    row[self.subdate] = new_date
        except OSError:
            for row in self.data:
                if type(row[self.subdate]) is not str:
                    raise TypeError("Date already formatted")
                if row[self.subdate]:
                    new_date = datetime.fromtimestamp(int(row[self.subdate]) / 1000,
                                                      tz=timezone.utc)
                    row[self.subdate] = new_date
        self.subdateformatted = True

    def format_id_trim(self, delimiter, index):
        for row in self.data:
            row[self.id] = row[self.id].split(delimiter)[index]

    def format_id_add(self, string_before, string_after):
        for row in self.data:
            row[self.id] = string_before + row[self.id] + string_after

    def conditional_extension(self, other, condition, extension_hours):
        if not self.duedate:
            raise RuntimeError("no due date defined previously")

        if not self.duedateformatted:
            raise ValueError("due date not formatted")

        extension_length = timedelta(hours=int(extension_hours))
        for row in self.data:
            for other_row in other.data:
                if row[self.id] == other_row[other.id] and condition(row, other_row):
                    new_date = row[self.duedate] + extension_length
                    row[self.duedate] = new_date

    def new_due_date_from(self, other):
        if not self.duedateformatted or not other.duedateformatted:
            raise ValueError("due date not formatted")

        for row in self.data:
            for other_row in other.data:
                if row[self.id] == other_row[other.id]:
                    row[self.duedate] = other_row[other.duedate]
                    print("extension given to " + row[self.id])

    def apply_late_penalty(self, multiplier, min_hrs_late=0, max_hrs_late=1000):
        if not self.duedateformatted or not self.subdateformatted:
            raise ValueError("not all dates formatted")

        for row in self.data:
            if row[self.subdate]:
                row[self.grade] = float(row[self.grade])
                delta = row[self.subdate] - row[self.duedate]
                if timedelta(hours=min_hrs_late) < delta <= timedelta(hours=max_hrs_late):
                    print('penalty applied to ' + row[self.id] + ": " + str(delta)
                          + ' hours late ' + str(float(row[self.grade]))
                          + "-->" + str(float(row[self.grade]) * multiplier))
                    row[self.grade] = float(row[self.grade]) * multiplier

    def take_highest_grade(self):
        if not self.grade:
            raise RuntimeError("missing grade column, review initialization")

        for row in self.data:
            if row[self.id] != 'remove_flag':
                high_index = 0
                high_grade = 0
                all_index = list()
                for count in range(len(self.data)):
                    if self.data[count][self.id] == row[self.id]:
                        all_index.append(count)
                        if float(self.data[count][self.grade]) >= high_grade:
                            high_index = count
                            high_grade = float(self.data[count][self.grade])
                for index in all_index:
                    if index != high_index:
                        self.data[index][self.id] = 'remove_flag'
        self.data = list(filter(lambda line: line[self.id] != 'remove_flag', self.data))

    def add_to_grade_import(self, destination):
        if not self.grade or not destination.grade:
            raise RuntimeError("missing one or more grade column, review initialization")

        for row in self.data:
            for dest_row in destination.data:
                if row[self.grade] and row[self.id] == dest_row[destination.id]:
                    if dest_row[destination.grade]:
                        dest_row[destination.grade] = float(dest_row[destination.grade]) \
                                                      + float(row[self.grade])
                    else:
                        dest_row[destination.grade] = float(row[self.grade])

    def print_to_csv(self, file_name):
        with open(file_name, 'w', newline='') as outputcsv:
            writer = csv.DictWriter(outputcsv, self.data[0].keys())
            writer.writeheader()
            writer.writerows(self.data)


tues_due_date = datetime.strptime(config["tues_date"], '%Y-%m-%d %H:%M:%S %z')
wedn_due_date = datetime.strptime(config["wedn_date"], '%Y-%m-%d %H:%M:%S %z')

extensions = GradeFile(config["exten"], config["extensions_file"])
extensions.format_duedates_from_string('%Y-%m-%d %H:%M')

learn_expo = GradeFile(config["learn"], config["learn_export_file"])
learn_expo.format_id_trim('#', 1)

print("\nMARMOSET REPORT: ")
marm_tues = GradeFile(config["marm"], config["marmoset_tues_file"])
marm_wedn = GradeFile(config["marm"], config["marmoset_wed_file"])
marm_data = marm_tues.combine_with(marm_wedn)
marm_data.format_subdates_from_timestamp()
marm_data.assign_due_date(tues_due_date)
marm_data.conditional_extension(learn_expo, lambda m_row, l_row:
                                l_row["ME101_chulls_pmteerts_1211_LAB"] == "241 Wednesday Lab", 24)
marm_data.new_due_date_from(extensions)
marm_data.apply_late_penalty(0.8, 0, 24)
marm_data.apply_late_penalty(0.6, 24, 48)
marm_data.apply_late_penalty(0, 48)
marm_data.take_highest_grade()
marm_data.add_to_grade_import(learn_expo)

print("\nCROWDMARK REPORT:")
crowd_tues = GradeFile(config["crowd"], config["crowdmark_tues_file"])
crowd_tues.assign_due_date(tues_due_date)
crowd_wedn = GradeFile(config["crowd"], config["crowdmark_wed_file"])
crowd_wedn.assign_due_date(wedn_due_date)
crowd_data = crowd_tues.combine_with(crowd_wedn)
crowd_data.format_subdates_from_string('%Y-%m-%d %H:%M:%S %Z')
crowd_data.format_id_trim('@', 0)
crowd_data.new_due_date_from(extensions)
crowd_data.apply_late_penalty(0.8, 0, 24)
crowd_data.apply_late_penalty(0.6, 24, 48)
crowd_data.apply_late_penalty(0, 48)
crowd_data.add_to_grade_import(learn_expo)

learn_expo.format_id_add('#', '')
learn_expo.print_to_csv(config["output_file"])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~TEST CASE 1~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
with open("A1_grade_import_BASELINE.csv", newline='') as csvFile:
    new_reader = csv.DictReader(csvFile)
    baseline = list(new_reader)

with open(config["output_file"], newline='') as csvFile:
    new_reader = csv.DictReader(csvFile)
    current = list(new_reader)

if len(baseline) != len(current):
    print("TEST_1 FAILED - different length lists")
else:
    for base, curr in zip(baseline, current):
        if base != curr:
            print("TEST_1 FAILED - line different")
            print("   current is " + curr[config["learn"]["id"]] + " vs "
                  + base[config["learn"]["id"]])
            print("   current is " + curr[config["learn"]["grade"]] + " vs "
                  + base[config["learn"]["grade"]])
