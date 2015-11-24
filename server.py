#
# A simple server for mortality data
#
# Requires the bottle framework
# (sufficient to have bottle.py in the same folder)
#
# run with:
#
#    python server.py 8000
#
# You can use any legal port number instead of 8000
# of course
#


from bottle import get, post, run, request, static_file, redirect
import os
import sys
import sqlite3

import traceback

from bottle import response
from json import dumps


MORTALITYDB = "mortality.db"


def pullData ():
    conn = sqlite3.connect(MORTALITYDB)
    cur = conn.cursor()

    try: 
        cur.execute("""SELECT year,
	        				Education, 
        					avg(Age_Value), 
	        				sex, 
	        				SUM(1) as total 
                       FROM mortality
                       WHERE Education!='' AND Education!='99'
                       GROUP BY year, Education, sex""")
        
        data = [{"year":int(year),
                 "education":int(education),
                 "avg": int(avg),
                 "gender":sex,
                 "total":total} for (year, education, avg, sex, total,) in  cur.fetchall()]
        conn.close()

        educations = list(set([r["education"] for r in data]))
        genders = list(set([r["gender"] for r in data]))
        avgs = list(set([r["avg"] for r in data]))

        return {"data":data, 
                "genders":genders,
                "educations":educations,
                "avg": avgs}

    except: 
        print "ERROR!!!"
        conn.close()
        raise

# average age of death
def questionOne():
    conn = sqlite3.connect(MORTALITYDB)
    cur = conn.cursor()

    try: 
        
        cur.execute("""SELECT year, Cause_Recode_39, avg(Age_Value)
                       FROM mortality
                       GROUP BY year, 
                    			Cause_Recode_39""")
        data = [{"year":int(year),
                 "avg": int(avg),
                 "cause":int(cause)
                } for (year, cause, avg,) in  cur.fetchall()]
        conn.close()

        return {"data":data}

    except: 
        print "ERROR!!!"
        conn.close()

# top cause of death
def questionTwo():
    conn = sqlite3.connect(MORTALITYDB)
    cur = conn.cursor()
    try: 
        cur.execute("""SELECT year, Cause_Recode_39,Age_Value , MAX(cause_death)
                        FROM (
                            SELECT year, Cause_Recode_39, Age_Value, Count(Cause_Recode_39) as cause_death
                            FROM mortality
                            GROUP BY year, Cause_Recode_39, Age_Value
                            )
                        GROUP BY Age_Value, year""")

        data = [{"year":int(year),
                 "cause":int(cause),
                 "maxDeath": maxDeath,
                 "age":Age} for (year, cause, Age, maxDeath,) in  cur.fetchall()]
        conn.close()
        return {"data":data}

    except: 
        print "ERROR!!!"
        conn.close()
        raise
  
       
@get('/data')
def data ():
    return pullData()


@get('/text')
def text ():
	one = questionOne()
	two = questionTwo()

	return {"one": one, "two":two}

@get('/<name>')
def static (name="project4.html"):
    return static_file(name, root='.')

def main (p):
    run(host='0.0.0.0', port=p)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(int(sys.argv[1]))
    else:
        print "Usage: server <port>"