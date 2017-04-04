#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

  python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@104.196.18.7/w4111
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.18.7/w4111"
#
DATABASEURI = "postgresql://gx2127:9667@104.196.18.7/w4111"

#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
 id serial,
 name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
 """
 This function is run at the beginning of every web request
 (every time you enter an address in the web browser).
 We use it to setup a database connection that can be used throughout the request.

 The variable g is globally accessible.
 """
 try:
  g.conn = engine.connect()
 except:
  print "uh oh, problem connecting to database"
  import traceback; traceback.print_exc()
  g.conn = None

@app.teardown_request
def teardown_request(exception):
 """
 At the end of the web request, this makes sure to close the database connection.
 If you don't, the database could run out of memory!
 """
 try:
  g.conn.close()
 except Exception as e:
  pass


def home_init():
   query = "select cname from country"
   cursor = g.conn.execute(query)
   countries = []
   for country in cursor:
       countries.append(country[0])
   cursor.close()
   return countries


@app.route('/', methods=['GET'])
def home():
 # DEBUG: this is debugging code to see what request looks like
 print request.args
 return render_template("home.html", Countries=home_init(), countries=home_init())


@app.route('/', methods=['POST','GET'])
def country_top_scorer():
    word=str(request.form.get('which_country'))
    max_min=request.form.get('max/min')
    year=request.form.get('bd')
    if max_min=='max':
        query = "select distinct foo3.pname, t.tname, l.lname, c.cname, foo3.pgoal,foo3.birthday from " \
                "(select p.pname, p.pid, p.pgoal, p.birthday from players p where p.pgoal in (select max(pgoal)from " \
                "(select t.tid, foo1.cid, foo1.lid, t.tname from team t, belongs_tl btl,(select c.cid, l.lid " \
                "from country c, league l, belongs_lc blc where c.cid=blc.cid and l.lid=blc.lid ) as foo1 where " \
                "t.tid=btl.tid and foo1.lid=btl.lid) as foo2, players p, plays_in py, country c where p.pid=py.pid " \
                "and foo2.tid=py.tid and c.cid=foo2.cid  and c.cname=%s)) as foo3, team t, league l, country c, " \
                "plays_in py, belongs_tl btl, belongs_lc blc where foo3.pid=py.tid and t.tid=py.tid and btl.tid=t.tid " \
                "and btl.lid=l.lid and blc.lid=l.lid and blc.cid=c.cid and foo3.birthday<=%s;"
    else:
        query = "select distinct foo3.pname, t.tname, l.lname, c.cname, foo3.pgoal, foo3.birthday from " \
                "(select p.pname, p.pid, p.pgoal, p.birthday from players p where p.pgoal in (select min(pgoal)from " \
                "(select t.tid, foo1.cid, foo1.lid, t.tname from team t, belongs_tl btl,(select c.cid, l.lid " \
                "from country c, league l, belongs_lc blc where c.cid=blc.cid and l.lid=blc.lid ) as foo1 where " \
                "t.tid=btl.tid and foo1.lid=btl.lid) as foo2, players p, plays_in py, country c where p.pid=py.pid " \
                "and foo2.tid=py.tid and c.cid=foo2.cid  and c.cname=%s)) as foo3, team t, league l, country c, " \
                "plays_in py, belongs_tl btl, belongs_lc blc where foo3.pid=py.tid and t.tid=py.tid and btl.tid=t.tid " \
                "and btl.lid=l.lid and blc.lid=l.lid and blc.cid=c.cid and foo3.birthday<=%s;"
    cursor=g.conn.execute(query, (word,year))
    result=[]
    for res in cursor:
        result.append(res)
    cursor.close()
    print request.args
    return render_template("home.html", scorers=result,Countries=home_init(), countries=home_init())

selected_countries=[]
selected_leagues=[]
selected_teams=[]

@app.route("/country_dd", methods=['GET', 'POST'])
def country_dd():
   query="select l.lname from country c, league l, belongs_lc blc where c.cid=blc.cid and l.lid=blc.lid;"
   country=str(request.form.get('which_country'))
   if(country!="all countries"):
       query=query[0:len(query)-1]+" and c.cname=%s;"
   cursor=g.conn.execute(query,country)
   leagues=[]
   for cur in cursor:
       leagues.append(cur[0])
   cursor.close()
   if(country not in selected_countries):
       selected_countries.append(country)
   return render_template('home.html', countries = selected_countries, leagues=leagues)

@app.route("/league_dd", methods=['GET','POST'])
def league_dd():
    query ="select t.tname from league l, belongs_tl tl, team t where l.lid = tl.lid and t.tid = tl.tid;"
    league = str(request.form.get('which_league'))
    if(league!="all leagues"):
        query=query[0:len(query)-1]+" and l.lname=%s;"
    cursor=g.conn.execute(query, league)
    teams=[]
    for cur in cursor:
        teams.append(cur[0])
    cursor.close()
    if(league not in selected_leagues):
        selected_leagues.append(league)
    return render_template('home.html', countries=selected_countries, leagues=selected_leagues, teams=teams)

@app.route("/team_dd", methods=['GET','POST'])
def team_dd():
    query = "select p.pname, p.prating, p.pgoal,p.birthday from plays_in pi, team t, players p where p.pid=pi.pid and pi.tid = t.tid;"
    team = str(request.form.get('which_team'))
    if(team!="all teams"):
        query=query[0:len(query)-1]+" and t.tname = %s;"
    cursor=g.conn.execute(query,team)
    players=[]
    for cur in cursor:
        players.append(cur)
	#cursor.close()
    if(team not in selected_teams):
        selected_teams.append(team)
	return render_template("home.html",countries=selected_countries, leagues=selected_leagues, teams=selected_teams, players = players)


@app.route("/champion_teams", methods=['GET','POST'])
def champion_teams():
    x=request.form.get('IsChamp')
    query="select t.tname from team t where t.tid " +x+ " (select t.tid from team t, belongs_tc btc where t.tid=btc.tid);"
    cursor=g.conn.execute(query, x)
    champion_teams=[]
    for cur in cursor:
        champion_teams.append(cur[0])
    cursor.close()
    return render_template('home.html', countries=home_init(),champion_teams=champion_teams)


@app.route("/match_history", methods=['GET', 'POST'])
def match_history():
    team=request.form.get('team')
    order=str(request.form.get('order'))
    query="select m.mid, m.mdate, t1.tname, m1.mname, t2.tname, m2.mname , m.home_goals, m.away_goals from match m, participate p, team t1, team t2, manager m1, manager m2, manages mag1, manages mag2 where m.mid=p.mid and t1.tid=p.tid and t2.tid=p.tid2 and m1.mid=mag1.mid and mag1.tid= t1.tid and m2.mid=mag2.mid and mag2.tid=t2.tid and (t1.tname= %s or t2.tname= %s) order by m.mdate;"
    if(order=="DESC"):
        query=query[0:len(query)-1]+" DESC"
    matches=[]
    cursor=g.conn.execute(query, (team ,team))
    for cur in cursor:
        matches.append(cur)
    cursor.close()
    return render_template('home.html', countries=home_init(), matches=matches)


@app.route('/insert', methods=['POST','GET'])
def insert():
    query = "select t.tname from league l, belongs_tl tl, team t where l.lid = tl.lid and t.tid = tl.tid;"
    cursor=g.conn.execute(query)
    teams=[]
    for cur in cursor:
        teams.append(cur[0])
    cursor.close()
    return  render_template('insert.html', teams = teams)

@app.route('/delete', methods=['POST','GET'])
def delete():
   return render_template('delete.html')

@app.route('/insert_player', methods=['POST', 'GET'])
def insert_player():
    pname = request.form['pname']
    pid = request.form['pid']
    prating = request.form['prating']
    pgoals = request.form['pgoals']
    team = request.form['teams']
    g.conn.execute("INSERT INTO players VALUES (%d, %d, %s, %d)", (pid, prating, pname, pgoals))
    g.conn.execute("INSERT INTO plays_in VALUES (%d, %d, %s)", (pid, tid, since))
    return render_template('insert.html')

@app.route('/insert_manager', methods=['POST', 'GET'])
def insert_manager():
 tname = request.form['tname']
 mid = request.form['mid']
 mname = request.form['mname']
 g.conn.execute("INSERT INTO manager VALUES (%s, %s)", (mid, mname))
 msg = "Record inserted successfully"
 return render_template("result.html", msg=msg)

@app.route('/list_manager', methods=['POST', 'GET'])
def list_manager():
 cursor = g.conn.execute('select * from manager;')
 result = []
 for res in cursor:
   result.append(res)  # can also be accessed using result[0]
 cursor.close()
 # return redirect(url_for('insert'))
 return render_template("list.html", result=result)

@app.route('/login')
def login():
  abort(401)
  this_is_never_executed()


if __name__ == "__main__":
 import click

 @click.command()
 @click.option('--debug', is_flag=True)
 @click.option('--threaded', is_flag=True)
 @click.argument('HOST', default='0.0.0.0')
 @click.argument('PORT', default=8111, type=int)
 def run(debug, threaded, host, port):
  """
  This function handles command line parameters.
  Run the server using:

     python server.py

  Show the help text using:

     python server.py --help

  """

  HOST, PORT = host, port
  print "running on %s:%d" % (HOST, PORT)
  app.run(host=HOST, port=PORT, debug=True, threaded=threaded)


 run()
