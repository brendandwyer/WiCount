import sqlite3 as lite
from sqlite3 import OperationalError
import glob, os
import numpy as np
import pandas as pd
from datetime import datetime
from dateutil.parser import parse
import math
from _nsis import err

def UpdateCollegeTable(occupancy_details):
    #-------------------------------------------------------
    #set up hard coding this will need to be passed in.
    #-------------------------------------------------------
    
    campus = "Belfield"
    building = "Computer Science"
    #print(occupancy_details)
    for x in range (0, len(occupancy_details[0])):
        #room_ID = ""
        try:
            sql_String = "SELECT room_id FROM college WHERE campus = '" + campus + \
                            "' AND building = '" + building + "' AND room = '" + occupancy_details[0][x] + "';"
            #print ("sql_String: ", sql_String)
            c.execute(sql_String)
            room_ID = c.fetchone()
            #print("room_ID: ", room_ID)
            if room_ID:
                sql_String = "UPDATE college SET occupancy=" + str(occupancy_details[1][x]) + \
                             " WHERE room_id=" + str(room_ID[0]) + ";" 
                c.execute(sql_String)
                room_ids.append(room_ID[0])
            else:
                room = [campus,building,occupancy_details[0][x],occupancy_details[1][x]]
                c.execute('INSERT INTO college (campus, building, room, occupancy) VALUES (?, ?, ?, ?)', room)
                c.execute(sql_String)
                room_ID = c.fetchone()[0]
                room_ids.append(room_ID)
        except OperationalError:
            print ("Command skipped: ", sql_String)
        con.commit()
    #print (room_ids)
    return room_ids

def UpdateSurveyTable(all_details):
    print(all_details)
    try:
        c.executemany('INSERT INTO survey VALUES (?,?,?,?)', all_details)
    except OperationalError:
        print ("Command skipped: ", all_details)
    con.commit()
    

def ConvertToCSV(file):
    data_xls = pd.read_excel(file, 'JustData', index_col=None)
    data_xls.to_csv('survey.csv', encoding='utf-8')
    
    
def GetRoomNo(room):
    #print("in GetRoomNo: ", room)
    if room != "":
        room = room.replace(".", "")
        room_no = room[:1] + "-"+ room[1:]
    else:
        room_no = ""
    #print ("room ", room_no)
    return room_no

def is_date(string):
    try: 
        parse(string)
        return True
    except ValueError as err:
        return False
    
def GetTime(data):
    # format the time for the database so it matches with other time formats
    data = data.split("-")
    time = data[0]
    #print ("data: ", type(time))
    if len(time) == 4:
        time = str("0") + str(time[:1]) + ":" + str(time[2:]) + str(":00")
    else:
        time = str(time[:2]) + ":" + str(time[3:]) + ":00"
    #print ("Time: ", time, " len: ", len(time))
    return time


con = lite.connect('wicount.sqlite3')
c=con.cursor()

# if the table doesn't exist create it.
try:
    c.execute ("create table if not exists survey(room_id INTEGER  NOT NULL, date DATETIME  NOT NULL, \
                day VARCHAR(3), percentage FLOAT, PRIMARY KEY (room_id, date));")
    c.execute ("create table if not exists college(room_id INTEGER PRIMARY KEY, campus VARCHAR(8), \
                building VARCHAR(16), room VARCHAR(5), occupancy INTEGER);")
except OperationalError:
    print("couldn't create the table")
con.commit()
     


#-------------------------------------------------------
#set up variables.
#-------------------------------------------------------
dayList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
timeList = ["9.00-10.00", "10.00-11.00", "11.00-12.00", "12.00-13.00", \
            "13.00-14.00", "14.00-15.00", "15.00-16.00", "16.00-17.00"]
full_details = []
room_ids = []
occupancy_details = []
full_list = []
day = "Mon"    #initialise variable
DateTime = ""
date = ""


# Got help from http://stackoverflow.com/questions/3964681/find-all-files-in-directory-with-extension-txt-in-python
os.chdir("Survey")
#set up hard codeing this will need to be passed in.
for file in glob.glob("*.xlsx"):
    sheet = pd.read_excel(file, 'JustData')
    sheet = sheet.dropna(how='all')
    sheet = sheet.dropna(axis='columns', how='all')
    #print(len(sheet))
    sheet.to_csv('survey.csv', encoding='utf-8')
    #print(type(sheet))
    dataArray = sheet.as_matrix()
    #print(dataArray)
    for data in dataArray:
        #print(data[0])
        if data[0] in dayList:
            day = data[0]
            day = day[:3]
            #print (day)
        elif data[1] == "Room No.":
            #print("build the room string")
            details = []
            if full_details == []:
                for x in range(2, len(data),1):
                    room_no = GetRoomNo(data[x])
                    details.append(room_no)
                    #print("velda: ", details)
                full_details.append(details)
                occupancy_details.append(details)
        elif data[0] == "Time":
            if len(occupancy_details) == 1:
                details = []
                for x in range(2, len(data),1):
                    details.append(data[x])
                    #print("velda: ", details)
                occupancy_details.append(details)
                #print(occupancy_details)
                room_ids = UpdateCollegeTable(occupancy_details)
        elif data[0] in timeList:
            details = []
            date_str = date + " " + GetTime(data[0])
            #date_str = datetime.strptime( date_str, '%b %d %Y %I:%M%p')
            for x in range(2, len(data),1):
                data_list = [room_ids[x-2], date_str, day, data[x]]
                details.append(data[x])
            #print("velda: ", details)
            full_details.append(details)
            full_list.append(data_list)
        elif "OCCU" in data[0]:
            continue
        else:
            date = parse(data[0])
            #print(date)
            date = date.strftime('%Y-%m-%d')
            #print(date)
            
        #end if
    UpdateSurveyTable(full_list)
    

con.close()
print("occupancy_details: ")
for x in range(0,len(occupancy_details)):
    print(occupancy_details[x])
print("")
print("full_details: ")
for x in range(0, len(full_details)):
    print(full_details[x])
print("")
print("full_list: ")
for x in range(0, len(full_list)):
    print(full_list[x])
print("")
print ("day: ", day)   



#     wb = openpyxl.load_workbook(file)
#     sheet = wb.get_sheet_by_name("JustData")
#          
#     sqlvalues = []
#     print(sheet)
#     print('velda ',sheet.max_column)
#     print("velda2 ", get_column_letter(sheet.max_column))
#     row_count = sheet.max_row - 1
#     print ('row_count ', row_count)
    #column_count = letter_to_index(sheet.max_col()) + 1
    #print('column_count ', column_count)
    #fullSheet = row_count + column_count
#     print(fullSheet)
#     table = np.array([[cell.value for cell in col] for col in sheet['A1':fullSheet]])
#     print(table)
#         for line in table:
#             print(line)
#             start_time = GetTime(line[0])
#             #build sql string
#             for i in range(1,len(line),2):
#                 db_values = [campus, building, room_no, GetDay(i), start_time, line[i], line[i+1]]
#                 sqlvalues.append(db_values)
#             try:
#                 c.executemany('INSERT INTO timetable VALUES (?,?,?,?,?,?,?)', sqlvalues)
#                 
#             except OperationalError:
#                 print ("Command skipped: ", sqlvalues)
#             print("done: ", sqlvalues)  
#             con.commit()
# cur.execute("DROP TABLE IF EXISTS Cars")
#     cur.execute("CREATE TABLE Cars(Id INT, Name TEXT, Price INT)")
#     cur.executemany("INSERT INTO Cars VALUES(?, ?, ?)", cars)
#con.close() 