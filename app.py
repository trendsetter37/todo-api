from flask import Flask, jsonify, abort, g, make_response, request
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

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
  ''' receiving json from client '''
  if not request.json or not 'title' in request.json:
    abort(400)
  db = get_db()
  sql = ''' INSERT INTO tasks (title, description, done) VALUES (?,?,?) '''
  insert = (request.json.get('title'), request.json.get('description', ''),request.json.get('done', 0))
  db.cursor().execute(sql, insert)
  db.commit()
  db.close()
  return jsonify({'status': 'Task Added'}), 201

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
  db = get_db()
  # find requested task
  sql = ''' SELECT * FROM tasks WHERE id=(?) '''
  cur = db.cursor()
  rows = cur.execute(sql, (task_id,)).fetchall()[0]
  row_id = rows['id'] 
  json = request.json
  
  # check data validity
  if len(rows) == 0:
    abort(404)
  if not request.json:
    print 'not a json'
    abort(400)
  if 'title' in request.json and type(request.json['title']) is not unicode:
    print 'Title was not unicode'
    abort(400)
  if 'description' in request.json and type(equest.json['description']) != unicode:
    print 'Description wasn\'t in unicode'
    abort(400)
  if 'done' in request.json and type(request.json['done']) is not bool:
    print 'done was not a boolean'
    abort(400)
  
  # Update database entry
  for key, val in json.items():
    cur.execute('''UPDATE tasks SET ''' + key +'''=(?) WHERE id=(?)''', (val, row_id))
  db.commit()
  return jsonify({'status':'Complete'}), 201

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
	pass

################
#Error Handlers#
################
@app.errorhandler(404)
def not_found(error):
  return make_response(jsonify({'error':'Task Not Found'}), 404)

@app.errorhandler(400)
def malformed(error):
  return make_response(jsonify({'error':'Malformed json object'}), 400)

if __name__ == '__main__':
  app.run(debug=True)
  
