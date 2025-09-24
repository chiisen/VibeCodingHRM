from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import os

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hrm-demo-secret-key-2024'
app.config['TEMPLATES_AUTO_RELOAD'] = True

# In-memory data storage
jobs = []
applications = []
employees = []
compensation_records = []

# Helper functions
def get_next_job_id():
    if not jobs:
        return 1
    return max(job['id'] for job in jobs) + 1

def get_next_application_id():
    if not applications:
        return 1
    return max(app['id'] for app in applications) + 1

def get_next_employee_id():
    if not employees:
        return 1
    return max(emp['id'] for emp in employees) + 1

# Sample data for demo
def initialize_sample_data():
    if not jobs:
        jobs.append({
            'id': 1,
            'title': 'Software Engineer',
            'department': 'Engineering',
            'positions': 3,
            'description': 'Develop and maintain web applications using modern technologies.'
        })
        jobs.append({
            'id': 2,
            'title': 'HR Manager',
            'department': 'Human Resources',
            'positions': 1,
            'description': 'Manage HR operations and employee relations.'
        })

    if not employees:
        employees.append({
            'id': 1,
            'name': 'John Doe',
            'employee_id': 'EMP001',
            'department': 'Engineering',
            'position': 'Software Engineer',
            'hire_date': '2024-01-15'
        })
        employees.append({
            'id': 2,
            'name': 'Jane Smith',
            'employee_id': 'EMP002',
            'department': 'Human Resources',
            'position': 'HR Specialist',
            'hire_date': '2024-02-01'
        })

@app.route('/')
def index():
    return render_template('index.html', jobs=jobs)

@app.route('/recruitment')
def recruitment():
    return render_template('recruitment.html', jobs=jobs, applications=applications)

@app.route('/add_job', methods=['GET', 'POST'])
def add_job():
    if request.method == 'POST':
        job = {
            'id': get_next_job_id(),
            'title': request.form['title'],
            'department': request.form['department'],
            'positions': int(request.form['positions']),
            'description': request.form['description']
        }
        jobs.append(job)
        flash('職缺新增成功！', 'success')
        return redirect(url_for('recruitment'))

    return render_template('add_job.html')

@app.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    job = next((j for j in jobs if j['id'] == job_id), None)
    if not job:
        flash('找不到該職缺！', 'error')
        return redirect(url_for('recruitment'))

    if request.method == 'POST':
        job['title'] = request.form['title']
        job['department'] = request.form['department']
        job['positions'] = int(request.form['positions'])
        job['description'] = request.form['description']
        flash('職缺更新成功！', 'success')
        return redirect(url_for('recruitment'))

    return render_template('edit_job.html', job=job)

@app.route('/delete_job/<int:job_id>')
def delete_job(job_id):
    global jobs
    jobs = [j for j in jobs if j['id'] != job_id]
    flash('職缺刪除成功！', 'success')
    return redirect(url_for('recruitment'))

@app.route('/apply_job/<int:job_id>', methods=['GET', 'POST'])
def apply_job(job_id):
    job = next((j for j in jobs if j['id'] == job_id), None)
    if not job:
        flash('找不到該職缺！', 'error')
        return redirect(url_for('recruitment'))

    if request.method == 'POST':
        application = {
            'id': get_next_application_id(),
            'job_id': job_id,
            'job_title': job['title'],
            'applicant_name': request.form['applicant_name'],
            'contact': request.form['contact'],
            'application_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        applications.append(application)
        flash('應徵成功！感謝您的申請。', 'success')
        return redirect(url_for('recruitment'))

    return render_template('apply_job.html', job=job)

@app.route('/employees')
def employees():
    search_query = request.args.get('search', '').strip()
    department_filter = request.args.get('department', '').strip()

    # Filter employees based on search criteria
    filtered_employees = employees

    if search_query:
        filtered_employees = [emp for emp in filtered_employees
                            if search_query.lower() in emp['name'].lower()]

    if department_filter:
        filtered_employees = [emp for emp in filtered_employees
                            if emp['department'] == department_filter]

    return render_template('employees.html', employees=filtered_employees, search_query=search_query, department_filter=department_filter)

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        employee = {
            'id': get_next_employee_id(),
            'name': request.form['name'],
            'employee_id': request.form['employee_id'],
            'department': request.form['department'],
            'position': request.form['position'],
            'hire_date': request.form['hire_date']
        }
        employees.append(employee)
        flash('員工新增成功！', 'success')
        return redirect(url_for('employees'))

    return render_template('add_employee.html')

@app.route('/edit_employee/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    employee = next((emp for emp in employees if emp['id'] == employee_id), None)
    if not employee:
        flash('找不到該員工！', 'error')
        return redirect(url_for('employees'))

    if request.method == 'POST':
        employee['name'] = request.form['name']
        employee['employee_id'] = request.form['employee_id']
        employee['department'] = request.form['department']
        employee['position'] = request.form['position']
        employee['hire_date'] = request.form['hire_date']
        flash('員工資料更新成功！', 'success')
        return redirect(url_for('employees'))

    return render_template('edit_employee.html', employee=employee)

@app.route('/delete_employee/<int:employee_id>')
def delete_employee(employee_id):
    global employees
    employees = [emp for emp in employees if emp['id'] != employee_id]
    flash('員工刪除成功！', 'success')
    return redirect(url_for('employees'))

@app.route('/compensation')
def compensation():
    return render_template('compensation.html', employees=employees, compensation_records=compensation_records)

@app.route('/edit_compensation/<int:employee_id>', methods=['GET', 'POST'])
def edit_compensation(employee_id):
    employee = next((emp for emp in employees if emp['id'] == employee_id), None)
    if not employee:
        flash('找不到該員工！', 'error')
        return redirect(url_for('compensation'))

    # Find existing compensation record or create new one
    comp_record = next((comp for comp in compensation_records
                        if comp['employee_id'] == employee_id), None)

    if not comp_record:
        comp_record = {
            'employee_id': employee_id,
            'employee_name': employee['name'],
            'base_salary': 0,
            'bonus': 0,
            'deductions': 0,
            'performance_rating': 'B',
            'comments': ''
        }
        compensation_records.append(comp_record)

    if request.method == 'POST':
        comp_record['base_salary'] = float(request.form['base_salary'])
        comp_record['bonus'] = float(request.form['bonus'])
        comp_record['deductions'] = float(request.form['deductions'])
        comp_record['performance_rating'] = request.form['performance_rating']
        comp_record['comments'] = request.form['comments']
        flash('薪酬資料更新成功！', 'success')
        return redirect(url_for('compensation'))

    return render_template('edit_compensation.html', employee=employee, comp_record=comp_record)

@app.route('/delete_compensation/<int:employee_id>')
def delete_compensation(employee_id):
    global compensation_records
    compensation_records = [comp for comp in compensation_records
                           if comp['employee_id'] != employee_id]
    flash('薪酬資料刪除成功！', 'success')
    return redirect(url_for('compensation'))

if __name__ == '__main__':
    initialize_sample_data()
    app.run(debug=True, host='0.0.0.0', port=5000)
