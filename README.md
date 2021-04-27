Built in Winter 2021 by Colin Chatfield under supervision of David Lau

# What it is
Tool for combining student grades, so that Learn can process them as a single grade item. Useful when using two different marking systems (like marmoset and crowdmark) on the same assignment. It can automatically apply late penalties and extensions. 

# How it works
Built around the GradeFile class. GradeFile objects are any sort of csv containing a list of students and associated information. They take in data from csv files as lists of dictionaries, then store which keys (i.e. columns) are of interest. Up to 4 keys initialized within the class; student id, grade, due date, and submission date. These topics should cover most if not all files being read. Information in other columns of interest (like a lab section determining due date for example) can be accessed manually using conditional functions. 

## General Process (main.py):
1. set up as many class objects as necessary
2. do operations on the data sets as necessary
3. combine data into a Learn export and print it to a csv file

# Detailed tutorial (based on combining marmoset and crowdmark grade for ME101 during Winter 2021):
1. download main.py, grade_file.py, and config.JSON into a new folder
2. download all necessary excel files, ensure they are converted to comma delimeted .csv files (refer to notes on specific programs below)
	* 6 csv files in total (if 2 sections in both marmoset and crowdmark are used)
3. check all values in config.JSON are correct
	* all file names must be updated (or file names updated to match config)
	* tuesday and wednesday dates must be updated (ALWAYS IN UTC TIME)
	* csv file "headers" should be checked. These are essentially the columns containing information we want. Marmoset/crowdmark headers likely won't change. Extension headers may change if you change the format of the spreadsheet. Learn grade header will change every assignment. 
4. open command line, change directory to folder, run main.py
5. Read any error messages that come up, if there is none then two files should have been created: a new ouput file (.csv, the one to be imported to learn) and a report file (.txt). 
6. Read report file. Report file is a tool to see obvious errors and to help debug. It should list every extension/penalty given to a submission (one student could have more than one extension/penalty given to each of their submissions). For marmoset, since all submissions are being compiled the late penalty listed may not be used in the students final grade. 
7. Once you are happy with the output files, import grades to learn.

# Notes on specific programs
* Crowdmark
	* Only one output option: "Export to CSV"
* Marmoset
	* Various output options, select "Print grades for ALL submissions in CSV format for spreadsheet use"
	* This one is used because it contains every submission, and we want to apply late penalties to every submission then pick the highest mark for each student
* Learn
	* export grades for the assignment so that the script can use that format for easy importing
	* NOTE: if all grade objects have been created at the start of the term, check that total points is correct for each assignment
	* Grades > Enter Grades > Export > Choose Grades to Export
	* Settings: Points grade, Username(which will be student id), Group membership (for due dates dependent on lab time)
* Extensions
	* We used an excel file on Sharepoint to record extensions
	* Note that the same .xlsx file can have multiple sheets for various assignments, simply save the sheet you want as a .csv file

# Notes on development:
All datetime values (due dates and submission dates) should be converted to UTC after reading from files.





