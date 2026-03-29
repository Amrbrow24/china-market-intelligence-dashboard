
# ============================================
# PROJECT 2: DATABASE-BACKED API (SQLite)
# No signup, no credit card, completely free
# ============================================

from datetime import datetime
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import sqlite3
import os
import threading
import time

# ============================================
# DATABASE SETUP (SQLite - Built into Python)
# ============================================

DB_NAME = "tasks.db"


def init_database():
    """Create database and table if they don't exist"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create tasks table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS tasks
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       title
                       TEXT
                       NOT
                       NULL,
                       description
                       TEXT,
                       priority
                       INTEGER
                       DEFAULT
                       1,
                       completed
                       BOOLEAN
                       DEFAULT
                       0,
                       created_at
                       TEXT
                       NOT
                       NULL,
                       updated_at
                       TEXT
                   )
                   ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized: tasks.db")


def get_all_tasks():
    """Get all tasks from database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, priority, completed, created_at, updated_at FROM tasks")
    rows = cursor.fetchall()
    conn.close()

    tasks = []
    for row in rows:
        tasks.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "priority": row[3],
            "completed": bool(row[4]),
            "created_at": row[5],
            "updated_at": row[6]
        })
    return tasks


def get_task_by_id(task_id):
    """Get a single task by ID"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, priority, completed, created_at, updated_at FROM tasks WHERE id = ?",
                   (task_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "priority": row[3],
            "completed": bool(row[4]),
            "created_at": row[5],
            "updated_at": row[6]
        }
    return None


def create_task(title, description, priority):
    """Create a new task in database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    created_at = str(datetime.now())

    cursor.execute('''
                   INSERT INTO tasks (title, description, priority, completed, created_at)
                   VALUES (?, ?, ?, ?, ?)
                   ''', (title, description, priority, False, created_at))

    task_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return get_task_by_id(task_id)


def update_task(task_id, title=None, description=None, priority=None, completed=None):
    """Update an existing task"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    updated_at = str(datetime.now())

    # Get current task
    current = get_task_by_id(task_id)
    if not current:
        conn.close()
        return None

    # Update only provided fields
    new_title = title if title is not None else current["title"]
    new_description = description if description is not None else current["description"]
    new_priority = priority if priority is not None else current["priority"]
    new_completed = completed if completed is not None else current["completed"]

    cursor.execute('''
                   UPDATE tasks
                   SET title       = ?,
                       description = ?,
                       priority    = ?,
                       completed   = ?,
                       updated_at  = ?
                   WHERE id = ?
                   ''', (new_title, new_description, new_priority, new_completed, updated_at, task_id))

    conn.commit()
    conn.close()

    return get_task_by_id(task_id)


def delete_task(task_id):
    """Delete a task from database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# ============================================
# API SERVER
# ============================================

class APIHandler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

    def do_GET(self):
        if self.path == '/':
            self.send_json({
                "message": "Project 2: Database-Backed API is running",
                "project": "Project 2 of 5",
                "database": "SQLite (permanent storage)",
                "status": "healthy",
                "endpoints": [
                    "GET /",
                    "GET /health",
                    "GET /tasks",
                    "GET /tasks?id=1",
                    "POST /tasks",
                    "PUT /tasks?id=1",
                    "DELETE /tasks?id=1"
                ]
            })

        elif self.path == '/health':
            self.send_json({
                "status": "healthy",
                "database": "SQLite",
                "tasks_count": len(get_all_tasks()),
                "timestamp": str(datetime.now())
            })

        elif self.path == '/tasks':
            tasks = get_all_tasks()
            self.send_json({
                "tasks": tasks,
                "count": len(tasks)
            })

        elif self.path.startswith('/tasks?id='):
            try:
                task_id = int(self.path.split('=')[1])
                task = get_task_by_id(task_id)
                if task:
                    self.send_json(task)
                else:
                    self.send_json({"error": f"Task {task_id} not found"}, 404)
            except ValueError:
                self.send_json({"error": "Invalid task ID"}, 400)

        else:
            self.send_json({"error": "Endpoint not found"}, 404)

    def do_POST(self):
        if self.path == '/tasks':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)

                title = data.get('title', 'Untitled')
                description = data.get('description', '')
                priority = data.get('priority', 1)

                task = create_task(title, description, priority)
                self.send_json({"message": "Task created", "task": task}, 201)
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_PUT(self):
        if self.path.startswith('/tasks?id='):
            try:
                task_id = int(self.path.split('=')[1])
                content_length = int(self.headers['Content-Length'])
                put_data = self.rfile.read(content_length)
                data = json.loads(put_data)

                task = update_task(
                    task_id,
                    title=data.get('title'),
                    description=data.get('description'),
                    priority=data.get('priority'),
                    completed=data.get('completed')
                )

                if task:
                    self.send_json({"message": "Task updated", "task": task})
                else:
                    self.send_json({"error": "Task not found"}, 404)
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_DELETE(self):
        if self.path.startswith('/tasks?id='):
            try:
                task_id = int(self.path.split('=')[1])
                if delete_task(task_id):
                    self.send_json({"message": "Task deleted"}, 204)
                else:
                    self.send_json({"error": "Task not found"}, 404)
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        else:
            self.send_json({"error": "Not found"}, 404)

    def log_message(self, format, *args):
        pass


# ============================================
# RUN THE SERVER
# ============================================

def run_server():
    port = 8000
    server_address = ('', port)
    httpd = HTTPServer(server_address, APIHandler)

    print("=" * 60)
    print("✅ PROJECT 2: DATABASE-BACKED API IS RUNNING!")
    print("=" * 60)
    print()
    print(f"🗄️  Database: SQLite ({DB_NAME})")
    print(f"🌐 Server: http://localhost:{port}")
    print()
    print("📋 Available endpoints:")
    print("   GET  /                - API information")
    print("   GET  /health          - Health check")
    print("   GET  /tasks           - Get all tasks")
    print("   POST /tasks           - Create a task")
    print("   GET  /tasks?id=1      - Get task with ID 1")
    print("   PUT  /tasks?id=1      - Update task")
    print("   DELETE /tasks?id=1    - Delete task")
    print()
    print("💾 Data is saved to tasks.db (permanent storage!)")
    print("=" * 60)
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)

    httpd.serve_forever()


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    # Initialize database
    init_database()

    # Show existing tasks
    tasks = get_all_tasks()
    if tasks:
        print(f"\n📊 Found {len(tasks)} existing task(s) in database.")
    else:
        print("\n📊 Database is empty. Create tasks with POST /tasks")

    # Run server
    run_server()