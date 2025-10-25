import os
from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Función para conectarse a la base de datos
def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),  # El host será el nombre del servicio de Docker
        database=os.environ.get('DB_NAME', 'postgres'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASS', 'mysecretpassword')
    )
    return conn

# Ruta para CREAR una nueva tarea
@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    title = data['title']
    description = data.get('description', '') # Descripción es opcional

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO tasks (title, description) VALUES (%s, %s) RETURNING id;',
                (title, description))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'id': new_id, 'title': title, 'description': description}), 201

# Ruta para LEER todas las tareas
@app.route('/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tasks;')
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    
    task_list = []
    for task in tasks:
        task_list.append({'id': task[0], 'title': task[1], 'description': task[2]})

    return jsonify(task_list)

# Ruta para LEER una sola tarea por ID
@app.route('/tasks/<int:id>', methods=['GET'])
def get_task(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tasks WHERE id = %s;', (id,))
    task = cur.fetchone()
    cur.close()
    conn.close()

    if task:
        return jsonify({'id': task[0], 'title': task[1], 'description': task[2]})
    else:
        return jsonify({'message': 'Task not found'}), 404

# Ruta para ACTUALIZAR una tarea por ID
@app.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    data = request.get_json()
    title = data['title']
    description = data.get('description')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE tasks SET title = %s, description = %s WHERE id = %s;',
                (title, description, id))
    conn.commit()
    updated_rows = cur.rowcount
    cur.close()
    conn.close()

    if updated_rows > 0:
        return jsonify({'id': id, 'title': title, 'description': description})
    else:
        return jsonify({'message': 'Task not found'}), 404

# Ruta para ELIMINAR una tarea por ID
@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM tasks WHERE id = %s;', (id,))
    conn.commit()
    deleted_rows = cur.rowcount
    cur.close()
    conn.close()

    if deleted_rows > 0:
        return jsonify({'message': 'Task deleted successfully'})
    else:
        return jsonify({'message': 'Task not found'}), 404

if __name__ == '__main__':
    # Inicializar la tabla si no existe (solo para fines de este ejemplo)
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error creating table: {e}")

    app.run(host='0.0.0.0', port=5000)