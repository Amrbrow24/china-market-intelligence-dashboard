# ============================================
# PROJECT 4: FULL-STACK WEB APP
# Complete web interface + API (Pure Python)
# No external packages needed!
# ============================================

from datetime import datetime
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import sqlite3
import webbrowser
import threading
import time

# ============================================
# DATABASE SETUP
# ============================================

DB_NAME = "tasks.db"


def init_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority INTEGER DEFAULT 1,
            completed BOOLEAN DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def get_all_tasks():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, description, priority, completed, created_at FROM tasks ORDER BY priority DESC, id DESC")
    rows = cursor.fetchall()
    conn.close()

    tasks = []
    for row in rows:
        tasks.append({
            "id": row[0],
            "title": row[1],
            "description": row[2] or "",
            "priority": row[3],
            "completed": bool(row[4]),
            "created_at": row[5]
        })
    return tasks


def create_task(title, description, priority):
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
    return task_id


def update_task_status(task_id, completed):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (completed, task_id))
    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


# ============================================
# HTML TEMPLATE (Beautiful Web Interface)
# ============================================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Manager - Project 4</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }

        .header p {
            opacity: 0.9;
        }

        .content {
            padding: 30px;
        }

        .add-task-form {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }

        .add-task-form input, .add-task-form select {
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            flex: 1;
            min-width: 150px;
        }

        .add-task-form button {
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: transform 0.2s;
        }

        .add-task-form button:hover {
            transform: translateY(-2px);
        }

        .task-list {
            list-style: none;
        }

        .task-item {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 15px;
            transition: all 0.2s;
        }

        .task-item:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }

        .task-item.completed {
            opacity: 0.6;
            background: #d1fae5;
        }

        .task-checkbox {
            width: 24px;
            height: 24px;
            cursor: pointer;
        }

        .task-info {
            flex: 1;
        }

        .task-title {
            font-weight: bold;
            font-size: 16px;
        }

        .task-description {
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }

        .task-priority {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
        }

        .priority-5 { background: #dc2626; color: white; }
        .priority-4 { background: #f97316; color: white; }
        .priority-3 { background: #eab308; color: #333; }
        .priority-2 { background: #22c55e; color: white; }
        .priority-1 { background: #6b7280; color: white; }

        .delete-btn {
            background: #dc2626;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s;
        }

        .delete-btn:hover {
            background: #b91c1c;
            transform: scale(1.05);
        }

        .stats {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            text-align: center;
            color: #666;
        }

        .empty-message {
            text-align: center;
            padding: 40px;
            color: #999;
        }

        .footer {
            background: #f8f9fa;
            padding: 15px;
            text-align: center;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #e0e0e0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Task Manager</h1>
            <p>Project 4: Full-Stack Web App | Python + SQLite</p>
        </div>

        <div class="content">
            <form class="add-task-form" onsubmit="addTask(event)">
                <input type="text" id="title" placeholder="Task title..." required>
                <input type="text" id="description" placeholder="Description (optional)">
                <select id="priority">
                    <option value="5">🔥 Priority 5 - Highest</option>
                    <option value="4">⚡ Priority 4 - High</option>
                    <option value="3" selected>📌 Priority 3 - Medium</option>
                    <option value="2">💡 Priority 2 - Low</option>
                    <option value="1">✅ Priority 1 - Lowest</option>
                </select>
                <button type="submit">+ Add Task</button>
            </form>

            <ul class="task-list" id="taskList">
                <div class="empty-message">Loading tasks...</div>
            </ul>

            <div class="stats" id="stats"></div>
        </div>

        <div class="footer">
            <p>✅ Data is saved permanently to SQLite database</p>
        </div>
    </div>

    <script>
        async function loadTasks() {
            const response = await fetch('/api/tasks');
            const data = await response.json();
            const tasks = data.tasks;
            const taskList = document.getElementById('taskList');
            const stats = document.getElementById('stats');

            if (tasks.length === 0) {
                taskList.innerHTML = '<div class="empty-message">✨ No tasks yet. Add your first task above!</div>';
                stats.innerHTML = '📊 0 tasks | Start organizing your work';
                return;
            }

            const completedCount = tasks.filter(t => t.completed).length;
            stats.innerHTML = `📊 ${tasks.length} tasks | ✅ ${completedCount} completed | ⏳ ${tasks.length - completedCount} pending`;

            taskList.innerHTML = tasks.map(task => `
                <li class="task-item ${task.completed ? 'completed' : ''}" data-id="${task.id}">
                    <input type="checkbox" class="task-checkbox" ${task.completed ? 'checked' : ''} onchange="toggleTask(${task.id}, this.checked)">
                    <div class="task-info">
                        <div>
                            <span class="task-title">${escapeHtml(task.title)}</span>
                            <span class="task-priority priority-${task.priority}">Priority ${task.priority}</span>
                        </div>
                        ${task.description ? `<div class="task-description">${escapeHtml(task.description)}</div>` : ''}
                        <div style="font-size: 11px; color: #999; margin-top: 5px;">${task.created_at}</div>
                    </div>
                    <button class="delete-btn" onclick="deleteTask(${task.id})">🗑️ Delete</button>
                </li>
            `).join('');
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        async function addTask(event) {
            event.preventDefault();
            const title = document.getElementById('title').value;
            const description = document.getElementById('description').value;
            const priority = document.getElementById('priority').value;

            await fetch('/api/tasks', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({title, description, priority: parseInt(priority)})
            });

            document.getElementById('title').value = '';
            document.getElementById('description').value = '';
            loadTasks();
        }

        async function toggleTask(id, completed) {
            await fetch(`/api/tasks/${id}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({completed})
            });
            loadTasks();
        }

        async function deleteTask(id) {
            if (confirm('Delete this task?')) {
                await fetch(`/api/tasks/${id}`, {method: 'DELETE'});
                loadTasks();
            }
        }

        loadTasks();
    </script>
</body>
</html>
'''


# ============================================
# HTTP SERVER (Handles both HTML and API)
# ============================================

class FullStackHandler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

    def send_html(self, content, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(content.encode())

    def do_GET(self):
        # Serve HTML page
        if self.path == '/' or self.path == '/index.html':
            self.send_html(HTML_TEMPLATE)

        # API: Get all tasks
        elif self.path == '/api/tasks':
            tasks = get_all_tasks()
            self.send_json({"tasks": tasks, "count": len(tasks)})

        else:
            self.send_html('<h1>404 - Page Not Found</h1><p><a href="/">Go to Task Manager</a></p>', 404)

    def do_POST(self):
        if self.path == '/api/tasks':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            title = data.get('title', 'Untitled')
            description = data.get('description', '')
            priority = data.get('priority', 3)

            task_id = create_task(title, description, priority)
            self.send_json({"message": "Task created", "id": task_id}, 201)
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_PUT(self):
        if self.path.startswith('/api/tasks/'):
            task_id = int(self.path.split('/')[-1])
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            data = json.loads(put_data)

            completed = data.get('completed', False)
            update_task_status(task_id, completed)
            self.send_json({"message": "Task updated"})
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_DELETE(self):
        if self.path.startswith('/api/tasks/'):
            task_id = int(self.path.split('/')[-1])
            delete_task(task_id)
            self.send_json({"message": "Task deleted"}, 204)
        else:
            self.send_json({"error": "Not found"}, 404)

    def log_message(self, format, *args):
        pass


def run_server():
    port = 8000
    server_address = ('', port)
    httpd = HTTPServer(server_address, FullStackHandler)

    print("=" * 60)
    print("✅ PROJECT 4: FULL-STACK WEB APP IS RUNNING!")
    print("=" * 60)
    print()
    print(f"🌐 Open your browser to: http://localhost:{port}")
    print()
    print("📋 Features:")
    print("   ✅ Beautiful web interface")
    print("   ✅ Add, complete, and delete tasks")
    print("   ✅ SQLite database (permanent storage)")
    print("   ✅ REST API backend")
    print("   ✅ Pure Python - no external packages!")
    print()
    print("=" * 60)
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)

    # Open browser automatically
    webbrowser.open(f'http://localhost:{port}')

    httpd.serve_forever()


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    init_database()
    print("\n📁 Database initialized: tasks.db")
    print("💾 Your tasks will be saved permanently!")
    print()
    run_server()