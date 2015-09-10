from flask import Flask, jsonify, abort, g, make_response
from db_tools import connect_to_database

app = Flask(__name__)
DATABASE = 'tasks.db'

def get_db():
  db = getattr(g, '_database', None)
  if db is None:
    db = g._database = connect_to_database()
  return db

@app.teardown_appcontext
def teardown_db(exception):
  db = getattr(g, '_database', None)
  if db is not None:
    db.close()

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
  ''' get all of your tasks '''
  db = get_db().cursor() 
  rows = db.execute('''SELECT * FROM tasks''')
  return jsonify({'tasks':rows.fetchall()})

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
	db = get_db().cursor()
	rows = db.execute('''SELECT * FROM tasks WHERE ID=(?)''',(task_id,)).fetchall()
	if len(rows) == 0:
		abort(404)
	return jsonify({'task':rows[0]})

################
#Error Handlers#
################
@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error':'Task Not Found'}), 404)

if __name__ == '__main__':
  app.run(debug=True)
  
