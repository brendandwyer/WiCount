import sqlite3 as sql
from sqlite3 import OperationalError
import json


def percentage_utilisation(room):

    con = sql.connect("wicount.sqlite3")
    cur = con.cursor()

    sqlstring = 'SELECT DISTINCT room, (CAST (COUNT(room) AS FLOAT) / \
        (SELECT DISTINCT COUNT(room) FROM analytics) *100) AS PercentageUtilised \
        FROM analytics \
        WHERE PredictedPercentage > 0 and Room = ?'

    try:
        percentage = cur.execute(sqlstring, (room,)).fetchall()
        con.commit()
        return percentage

    except OperationalError:
        con.close()
        return "An error occurred while calculating percentage utilisation"
    except Exception as e:
        print(e)


def greater_lesser(numberpeople, comparison):

    con = sql.connect("wicount.sqlite3")
    cur = con.cursor()

    if comparison == '>=':
        operator = '>='
    else:
        operator = '<='

    sqlstring = "SELECT room, date\
    FROM analytics \
    WHERE ? {} ((0.1 * PredictedPercentage) * Capacity)".format(operator)

    # Have to use string operation because ">=" is an SQL parameter.

    roomlist = cur.execute(sqlstring, (numberpeople,)).fetchall()
    con.commit()
    return roomlist


def list_occupancy_x(occupancy):
    # List rooms where occupancy = 0/50/100
    con = sql.connect("wicount.sqlite3")
    cur = con.cursor()

    # Select full rooms
    sqlstring = 'SELECT room, date \
    from analytics \
    WHERE PredictedPercentage = ?'

    try:
        roomlist = cur.execute(sqlstring, (occupancy,)).fetchall()
        con.commit()
        return json.dumps([dict(ix) for ix in roomlist])

    except OperationalError:
        con.close()
        return "An error occurred while fetching rooms of occupancy {}%.".format(occupancy)

    except Exception as e:
        print(e)


# print(percentage_utilisation("B-004"))
# print(greater_lesser(10, '>='))

print('List occupancy:', list_occupancy_x("50"))


