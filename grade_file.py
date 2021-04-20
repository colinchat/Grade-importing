import csv
from datetime import datetime, timedelta, timezone


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
        if due_datetime.tzinfo is None:
            raise TypeError("due_datetime must contain timezone information")

        if self.duedate is None:
            self.duedate = 'duedate'

        for row in self.data:
            row[self.duedate] = due_datetime

        self.duedateformatted = True

    def format_duedates_from_string(self, src_format, src_timezone):
        if self.duedateformatted:
            raise TypeError("already formatted due dates")

        if self.duedate is None or self.duedate not in self.data[0].keys():
            raise KeyError("Due date column not recognized, review initialization")

        for row in self.data:
            if row[self.duedate] and row[self.duedate] != '#N/A':
                # reads datetime from string
                new_date = datetime.strptime(row[self.duedate], src_format)
                # confirms that timezone is attached
                if new_date.tzinfo is None:
                    new_date = new_date.replace(tzinfo=src_timezone)
                # if timezone is not UTC then convert to UTC
                if new_date.tzinfo != timezone.utc:
                    new_date = new_date.astimezone(tz=timezone.utc)
                row[self.duedate] = new_date

        self.duedateformatted = True

    def format_subdates_from_string(self, src_format, src_timezone):
        if self.subdateformatted:
            raise TypeError("already formatted sub dates")

        if self.subdate is None or self.subdate not in self.data[0].keys():
            raise KeyError("Due date column not recognized, review initialization")

        for row in self.data:
            if row[self.subdate]:
                # reads datetime from string
                new_date = datetime.strptime(row[self.subdate], src_format)
                # confirms that timezone is attached
                if new_date.tzinfo is None:
                    new_date = new_date.replace(tzinfo=src_timezone)
                # if timezone is not UTC then convert to UTC
                if new_date.tzinfo != timezone.utc:
                    new_date = new_date.astimezone(tz=timezone.utc)
                row[self.subdate] = new_date

        self.subdateformatted = True

    def format_duedates_from_timestamp(self, src_timezone):
        if self.duedateformatted:
            raise TypeError("already formatted due dates")

        if self.duedate is None or self.duedate not in self.data[0].keys():
            raise KeyError("Due date column not recognized, review initialization")

        try:
            for row in self.data:
                if row[self.duedate]:
                    # reads date from string, assigns timezone
                    new_date = datetime.fromtimestamp(int(row[self.duedate]),
                                                      tz=src_timezone)
                    # if timezone is not UTC then convert to UTC
                    if new_date.tzinfo != timezone.utc:
                        new_date = new_date.astimezone(tz=timezone.utc)
                    row[self.duedate] = new_date
        except OSError:
            for row in self.data:
                if row[self.duedate]:
                    # reads date from string, assigns timezone
                    new_date = datetime.fromtimestamp(int(row[self.duedate]) / 1000,
                                                      tz=src_timezone)
                    # if timezone is not UTC then convert to UTC
                    if new_date.tzinfo != timezone.utc:
                        new_date = new_date.astimezone(tz=timezone.utc)
                    row[self.duedate] = new_date

        self.duedateformatted = True

    def format_subdates_from_timestamp(self, src_timezone):
        if self.subdateformatted:
            raise TypeError("already formatted sub dates")

        if self.subdate is None or self.subdate not in self.data[0].keys():
            raise KeyError("Due date column not recognized, review initialization")

        try:
            for row in self.data:
                if row[self.subdate]:
                    # reads date from string, assigns timezone
                    new_date = datetime.fromtimestamp(int(row[self.subdate]),
                                                      tz=src_timezone)
                    # if timezone is not UTC then convert to UTC
                    if new_date.tzinfo != timezone.utc:
                        new_date = new_date.astimezone(tz=timezone.utc)
                    row[self.subdate] = new_date
        except OSError:
            for row in self.data:
                if row[self.subdate]:
                    # reads date from string, assigns timezone
                    new_date = datetime.fromtimestamp(int(row[self.subdate]) / 1000,
                                                      tz=timezone.utc)
                    # if timezone is not UTC then convert to UTC
                    if new_date.tzinfo != timezone.utc:
                        new_date = new_date.astimezone(tz=timezone.utc)
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

    def apply_late_penalty(self, subtraction, min_hrs_late=0, max_hrs_late=1e7):
        if not self.duedateformatted or not self.subdateformatted:
            raise ValueError("not all dates formatted")

        for row in self.data:
            if row[self.subdate] and row[self.duedate]:
                delta = row[self.subdate] - row[self.duedate]
                if type(row[self.grade]) is not float:
                    row[self.grade] = float(row[self.grade])
                if timedelta(hours=min_hrs_late) < delta <= timedelta(hours=max_hrs_late):
                    newgrade = max(row[self.grade] - subtraction, 0)
                    output = 'penalty applied to {o1}: {o2} hrs late {o3: .2f} --> {o4: .2f}'
                    print(output.format(o1=row[self.id], o2=delta,
                                        o3=row[self.grade], o4=newgrade))
                    row[self.grade] = newgrade

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



