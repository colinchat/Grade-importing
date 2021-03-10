Built in Winter 2021 by Colin Chatfield under supervision of David Lau

Tool for combining student grades, so that Learn can process them as a single grade item. Useful when using two different marking systems (like marmoset and crowdmark) on the same assignment. It can automatically apply late penalties and extensions. 

Built around the GradeFile class. GradeFile objects are any sort of csv containing a list of students and associated information. They take in data from csv files as lists of dictionaries, then store which keys (i.e. columns) are of interest. Up to 4 keys initialized within the class; student id, grade, due date, and submission date. These topics should cover most if not all files being read. Information in other columns of interest (like a lab section determining due date for example) can be accessed manually using conditional functions. 

How to setup (create new main.py):
 1. read and understand the GradeFile class
 2. set up as many class objects as necessary
 3. set up config.JSON with correct headers and date formats
 4. do operations on the data as necessary
 5. combine data into a Learn export and print it to a csv file

How to use it (with main.py set up for ME101 winter 2021):
 1. create a folder for the assignment
 2. copy all required .py files into that folder (main.py, grade_file.py)
 3. convert all required excel files to comma delimited (.csv) files
 4. copy all required .csv files into that folder (crowdmark exports, marmoset exports, extensions, learn export)
 5. update config file values (new learn header, file names, due dates)
 6. run main.py 
 7. review report.txt and final grade file to make sure it worked as expected

Notes on development:
All datetime values (due dates and submission dates) should be converted to UTC after reading from files.





