from flask import Flask, jsonify, abort, g, make_response, request, url_for
from flask.ext.httpauth import HTTPBasicAuth
from db_tools import connect_to_database

app = Flask(__name__)
DATABASE = 'tasks.db'
auth = HTTPBasicAuth()
_errors = {}

#############
# Utilities #
#############

@auth.get_password
def get_password(username):
  ''' callback function the extension will use to get a password
      This will eventually use a database '''
  if username == 'javis':
    return 'testpassword'
  return None

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

def make_public_uri(task):
    ''' Receives task as dictionary '''
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id=task[field], _external=True)
        else:
            new_task[field] = task[field]
    return new_task

##########
# Routes #
##########

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
  ''' get all of your tasks '''
  db = get_db().cursor()
  rows = db.execute('''SELECT * FROM tasks''')
  return jsonify({'tasks': [make_public_uri(task) for task in rows.fetchall()]})

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
@auth.login_required
def get_task(task_id):
  db = get_db().cursor()
  rows = db.execute('''SELECT * FROM tasks WHERE ID=(?)''',(task_id,)).fetchall()
  if len(rows) == 0:
	abort(404)
  return jsonify({'task':make_public_uri(rows[0])})

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
@auth.login_required
def create_task():
  ''' receiving json from client '''
  global _errors
  if not request.json:
    _errors['not_json'] = True
    abort(400)
  if not 'title' in request.json:
    _errors['missing_title'] = True
    abort(400)
  db = get_db()
  sql = ''' INSERT INTO tasks (title, description, done) VALUES (?,?,?) '''
  insert = (request.json.get('title'), request.json.get('description', ''),request.json.get('done', 0))
  db.cursor().execute(sql, insert)
  db.commit()
  db.close()
  return jsonify({'status': 'Task Added'}), 201

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
@auth.login_required
def update_task(task_id):
  global _errors
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
    _errors['not_json'] = True
    abort(400)
  if 'title' in request.json and type(request.json['title']) is not unicode:
    _errors['title_unicode_issue'] = True
    abort(400)
  if 'description' in request.json and type(equest.json['description']) != unicode:
    _errors['description_unicode_issue'] = True
    abort(400)
  if 'done' in request.json and type(request.json['done']) is not bool:
    _errors['done_field_issue'] = True
    abort(400)

  # Update database entry
  for key, val in json.items():
    cur.execute('''UPDATE tasks SET ''' + key +'''=(?) WHERE id=(?)''', (val, row_id))
  db.commit()
  return jsonify({'status':'Complete'}), 201

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
@auth.login_required
def delete_task(task_id):
  db = get_db()
  cur = db.cursor()
  sql = '''SELECT * FROM tasks WHERE id=(?)'''
  row = cur.execute(sql, (task_id,)).fetchall()[0]

  if len(row) == 0:
    abort(404)
  sql = '''DELETE FROM tasks WHERE id=(?)'''
  cur.execute(sql,(task_id,))
  db.commit()
  return jsonify({'status':'Deletion complete'}), 205


##################
# Error Handlers #
##################

@app.errorhandler(404)
def not_found(error):
  print 'Error: {}'.format(error)
  return make_response(jsonify({'error':'Task Not Found'}), 404)

@app.errorhandler(400)
def malformed(error):
  global _errors
  errors = []
  if 'not_json' in _errors and _errors['not_json']:
    errors.append(u'json object was not sent by client')
    _errors['not_json'] = False
  if 'missing_title' in _errors and _errors['missing_title']:
    errors.append(u'json task did not have a title')
    _errors['missing_title'] = False
  if 'title_unicode_issue' in _errors and _errors['title_unicode_issue']:
    errors.append(u'title was not unicode')
    _errors['title_unicode_issue'] = False
  if 'description_unicode_issue' in _errors and _errors['description_unicode_issue']:
    errors.append(u'description was not unicode')
    _errors['description_unicode_issue'] = False
  if 'done_field_issue' in _errors and _errors['done_field_issue']:
    errors.append(u'done field did not contain a boolean')
    _errors['done_field_issue'] = False

  return make_response(jsonify({'errors':errors}), 400)

@auth.error_handler
def unauthorized():
  return make_response(jsonify({'error':'Unauthorized Access'}), 401)


if __name__ == '__main__':
  app.run(debug=True)
