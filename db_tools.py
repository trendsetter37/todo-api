#!todo/bin/python

import sqlite3
import os
import sys
import subprocess

def delete_db():

  subprocess.call(['rm','tasks.db'])

def create_db():
  ''' done field will represent the True --> 1 or False --> 0 '''
  conn = sqlite3.connect('tasks.db')
  db = conn.cursor()
  sql = ''' CREATE TABLE tasks (id INTEGER PRIMARY KEY,
                                title TEXT,
                                description BLOB,
                                done INTEGER) '''
  db.execute(sql)
  conn.commit()
  conn.close()

def init_db_populate():
  conn = sqlite3.connect('tasks.db')
  db = conn.cursor()
  tasks = [(u'Buy groceries', u'Milk, Cheese, Pizza, Fruit, Tylenol', 0),
           (u'Learn Python', u'Need to find a good Python tutorial on the web',0)]
  db.executemany(''' INSERT INTO tasks (title, description, done) VALUES (?,?,?)''', tasks)
  conn.commit()
  conn.close()

if __name__ == '__main__':
  if len(sys.argv) > 1:
    arg = sys.argv[1]
    if arg == 'delete':
      if not os.path.exists('tasks.db'):
         print 'Database does not exist'
         sys.exit()
      delete_db()
      print 'Database deleted'
    elif arg == 'create':
      if os.path.exists('tasks.db'):
        print 'Database already exists'
        sys.exit()
      create_db()
      init_db_populate()
      print 'Database created and populated'
    elif len(sys.argv) == 2 and sys.argv[2] == 'populate':
      inti_db_populate()
      print 'Database populated'
  else:
    print 'Usage: python db_tools.py [create|delete,[populate]]'
