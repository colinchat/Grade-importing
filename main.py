import json
import sys
from datetime import datetime, timedelta, timezone
from grade_file import GradeFile
from test_cases import areequal


reportfile = "report " + datetime.now().strftime('%Y-%m-%d %H.%M.%S') + ".txt"
sys.stdout = open(reportfile, 'w')

configFile = open('config.json', 'r')
config = json.load(configFile)
configFile.close()

tues_due_date = datetime.strptime(config["tues_date"], '%Y-%m-%d %H:%M:%S %z')
wedn_due_date = datetime.strptime(config["wedn_date"], '%Y-%m-%d %H:%M:%S %z')

extensions = GradeFile(config["exten"], config["extensions_file"])
extensions.format_duedates_from_string('%Y-%m-%d %H:%M', timezone(-timedelta(hours=5)))

learn_expo = GradeFile(config["learn"], config["learn_export_file"])
learn_expo.format_id_trim('#', 1)

print("\nMARMOSET REPORT: ")
marm_tues = GradeFile(config["marm"], config["marmoset_tues_file"])
marm_wedn = GradeFile(config["marm"], config["marmoset_wed_file"])
marm_data = marm_tues.combine_with(marm_wedn)
marm_data.format_subdates_from_timestamp(timezone.utc)
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
crowd_data.format_subdates_from_string('%Y-%m-%d %H:%M:%S %Z', timezone.utc)
crowd_data.format_id_trim('@', 0)
crowd_data.new_due_date_from(extensions)
crowd_data.apply_late_penalty(0.8, 0, 24)
crowd_data.apply_late_penalty(0.6, 24, 48)
crowd_data.apply_late_penalty(0, 48)
crowd_data.add_to_grade_import(learn_expo)

learn_expo.format_id_add('#', '')
outputfile = config["output_file"] + " " + datetime.now().strftime('%Y-%m-%d %H.%M.%S') + ".csv"
learn_expo.print_to_csv(outputfile)

areequal("A1_grade_import_BASELINE.csv", outputfile)

sys.stdout.close()
