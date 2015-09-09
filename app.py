from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)
#conn = sqlite3.connect('tasks.db')
#db = conn.cursor()

@app.route('/todo/api/v1.0/tasks')
def get_tasks():
  conn = sqlite3.connect('tasks.db')
  db = conn.cursor() 
  rows = db.execute('''SELECT * FROM tasks''')
  conn.close()
  return jsonify({'tasks':rows.fetchall()})

if __name__ == '__main__':
  app.run(debug=True)
  
