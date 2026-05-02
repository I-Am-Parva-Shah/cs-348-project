from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import time

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasktracker.db'
import os

if os.environ.get('GAE_ENV') == 'standard':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/tasktracker.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasktracker.db'
db = SQLAlchemy(app)

class Project(db.Model):
    project_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tasks = db.relationship('Task', backref='project', lazy=True)


class Developer(db.Model):
    developer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tasks = db.relationship('Task', backref='developer', lazy=True)

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), nullable=False, index=True)
    estimated_hours = db.Column(db.Integer, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id'), nullable=False, index=True)
    developer_id = db.Column(db.Integer, db.ForeignKey('developer.developer_id'), nullable=False, index=True)

@app.route('/', methods=['GET', 'POST'])
def manage_tasks():
    # Requirement 2: Filtering data and generating report
    filter_project = request.args.get('filter_project')
    filter_developer = request.args.get('filter_developer')
    min_hours = request.args.get('min_hours')
    max_hours = request.args.get('max_hours')

    # Start with base query
    query = Task.query

    # Apply filters if provided
    if filter_project:
        query = query.filter(Task.project_id == filter_project)
    if filter_developer:
        query = query.filter(Task.developer_id == filter_developer)
    if min_hours:
        query = query.filter(Task.estimated_hours >= int(min_hours))
    if max_hours:
        query = query.filter(Task.estimated_hours <= int(max_hours))

    # Execute the query
    tasks = query.all()

    # Retrieval for the UI dropdowns
    projects = Project.query.all()
    developers = Developer.query.all()

    # Calculate statistics for the report
    total_hours = sum(task.estimated_hours for task in tasks)

    return render_template('index.html', tasks=tasks, projects=projects,
                           developers=developers, total_hours=total_hours)

@app.route('/add_project', methods=['POST'])
def add_project():
    new_project = Project(name=request.form['project_name'])
    db.session.add(new_project)
    db.session.commit()
    return redirect(url_for('manage_tasks'))

@app.route('/add_developer', methods=['POST'])
def add_developer():
    new_developer = Developer(name=request.form['developer_name'])
    db.session.add(new_developer)
    db.session.commit()
    return redirect(url_for('manage_tasks'))


@app.route('/delete_project/<int:id>', methods=['POST'])
def delete_project(id):
    # First, safely delete any tasks associated with this project to prevent database errors
    Task.query.filter_by(project_id=id).delete()

    # Now delete the project itself
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('manage_tasks'))


@app.route('/delete_developer/<int:id>', methods=['POST'])
def delete_developer(id):
    # First, safely delete any tasks associated with this developer
    Task.query.filter_by(developer_id=id).delete()

    # Now delete the developer
    developer = Developer.query.get_or_404(id)
    db.session.delete(developer)
    db.session.commit()
    return redirect(url_for('manage_tasks'))

@app.route('/add', methods=['POST'])
def add_task():
    # Requirement 1: Add to main table
    new_task = Task(
        title=request.form['title'],
        status=request.form['status'],
        estimated_hours=int(request.form['hours']),
        project_id=int(request.form['project_id']),
        developer_id=int(request.form['developer_id'])
    )
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('manage_tasks'))


@app.route('/delete/<int:id>')
def delete_task(id):
    # Requirement 1: Delete from main table
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('manage_tasks'))


@app.route('/update/<int:id>', methods=['POST'])
def update_task(id):
    # Requirement 1: Update multiple fields in main table
    task = Task.query.get_or_404(id)

    task.title = request.form['title']
    task.status = request.form['status']
    task.estimated_hours = int(request.form['hours'])
    task.project_id = int(request.form['project_id'])
    task.developer_id = int(request.form['developer_id'])

    # Delay only for demonstrating isolation
    time.sleep(5)

    db.session.commit()
    return redirect(url_for('manage_tasks'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)


# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()  # Creates the tables automatically
#     app.run(debug=True)
