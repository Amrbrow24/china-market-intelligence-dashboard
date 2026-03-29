# ============================================
# PROFESSIONAL API - RUNS WITH GREEN BUTTON
# Your API is ready! Manual GitHub upload instructions below.
# ============================================

from datetime import datetime
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser
import os

# ============================================
# YOUR API CODE
# ============================================

tasks_db = {}
task_counter = 1


class APIHandler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

    def do_GET(self):
        global tasks_db, task_counter

        if self.path == '/':
            self.send_json({
                "message": "My Professional API is running",
                "status": "healthy",
                "project": "Project 1 of 5",
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
                "tasks_count": len(tasks_db),
                "timestamp": str(datetime.now())
            })

        elif self.path == '/tasks':
            tasks_list = list(tasks_db.values())
            self.send_json({
                "tasks": tasks_list,
                "count": len(tasks_list)
            })

        elif self.path.startswith('/tasks?id='):
            try:
                task_id = int(self.path.split('=')[1])
                if task_id in tasks_db:
                    self.send_json(tasks_db[task_id])
                else:
                    self.send_json({"error": f"Task {task_id} not found"}, 404)
            except:
                self.send_json({"error": "Invalid task ID"}, 400)

        else:
            self.send_json({"error": "Endpoint not found"}, 404)

    def do_POST(self):
        global tasks_db, task_counter

        if self.path == '/tasks':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)

                task = {
                    "id": task_counter,
                    "title": data.get('title', 'Untitled'),
                    "description": data.get('description', ''),
                    "priority": data.get('priority', 1),
                    "completed": False,
                    "created_at": str(datetime.now())
                }

                tasks_db[task_counter] = task
                task_counter += 1

                self.send_json({"message": "Task created", "task": task}, 201)
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_PUT(self):
        global tasks_db

        if self.path.startswith('/tasks?id='):
            try:
                task_id = int(self.path.split('=')[1])

                if task_id not in tasks_db:
                    self.send_json({"error": "Task not found"}, 404)
                    return

                content_length = int(self.headers['Content-Length'])
                put_data = self.rfile.read(content_length)
                data = json.loads(put_data)

                task = tasks_db[task_id]
                if 'title' in data:
                    task['title'] = data['title']
                if 'description' in data:
                    task['description'] = data['description']
                if 'priority' in data:
                    task['priority'] = data['priority']
                if 'completed' in data:
                    task['completed'] = data['completed']
                task['updated_at'] = str(datetime.now())

                self.send_json({"message": "Task updated", "task": task})
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_DELETE(self):
        global tasks_db

        if self.path.startswith('/tasks?id='):
            try:
                task_id = int(self.path.split('=')[1])

                if task_id not in tasks_db:
                    self.send_json({"error": "Task not found"}, 404)
                    return

                del tasks_db[task_id]
                self.send_json({"message": "Task deleted"}, 204)
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
    print("✅ PROJECT 1: PROFESSIONAL API IS RUNNING!")
    print("=" * 60)
    print()
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
    print("=" * 60)
    print("📖 Open your browser to: http://localhost:8000")
    print("=" * 60)
    print()
    print("🛑 Press Ctrl+C to stop the server")
    print()

    # Open browser automatically
    webbrowser.open('http://localhost:8000')

    httpd.serve_forever()


# ============================================
# INSTRUCTIONS FOR GITHUB
# ============================================

def show_github_instructions():
    print("=" * 60)
    print("📦 HOW TO UPLOAD TO GITHUB")
    print("=" * 60)
    print()
    print("Your API is working! To upload to GitHub:")
    print()
    print("1️⃣ Go to: https://github.com/Amrbrow24/python-rest-api")
    print()
    print("2️⃣ Click the 'Add file' button")
    print()
    print("3️⃣ Click 'Upload files'")
    print()
    print("4️⃣ Drag and drop your 'main.py' file")
    print(f"   Location: C:\\Users\\abdul_wse6qyg\\PycharmProjects\\PythonProject2\\main.py")
    print()
    print("5️⃣ Scroll down and click 'Commit changes'")
    print()
    print("=" * 60)
    print("🎯 Your Project 1 is COMPLETE!")
    print("=" * 60)
    print()


# ============================================
# MAIN - Click the green Run button!
# ============================================

if __name__ == "__main__":
    import threading
    import time

    # Show GitHub instructions
    show_github_instructions()

    # Run the API server
    run_server()