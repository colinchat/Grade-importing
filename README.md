What:
Tool for combining lists of student grades, so that Learn can process them as a single grade item. It can automatically apply late penalties and extensions. 

Why:
Useful when using two different marking systems (like marmoset and crowdmark). 

Overview:
Built around the GradeFile class. GradeFile handles any sort of csv containing a list of students and associated information. It works by taking in data from csv files as lists of dictionaries, then storing which keys (i.e. columns) are of interest. Up to 4 keys initialized within the class; student id, grade, due date, and submission date. These topics should cover most if not all files being read. Information in other columns of interest (like a lab section determining due date for example) can be accessed manually using conditional functions. 

Note on time:
All date values are stored as datetime objects. All datetime objects are converted to UTC after assigning them. Should new functions be added, this rule must be followed to comply with base functions. 

When:
Built in Winter 2021

Who:
Built by Colin Chatfield under supervision of David Lau