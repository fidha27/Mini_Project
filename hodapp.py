from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['miniproject']

# Routes

# Home Page (Login Page)
@app.route('/')
def index():
    return render_template('login.html')

# HOD Login Route
@app.route('/hod_login', methods=['POST'])
def hod_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Verify HOD credentials
    hod = db.departments.find_one({"hod_username": username, "hod_password": password})
    if hod:
        session['hod_username'] = username  # Store HOD username in session
        session['dept_code'] = hod['dept_code']  # Store department code in session
        return jsonify({"success": True, "redirect_url": url_for('hod')})
    else:
        return jsonify({"success": False})

# HOD Dashboard Route
@app.route('/hod')
def hod():
    if 'hod_username' not in session:
        return redirect(url_for('index'))  # Redirect to login if not logged in

    # Fetch batch and advisor data from the database
    batches = list(db.batch.find({}, {'_id': 0, 'batch_id': 1, 'adname': 1}))
    return render_template('hod.html', batches=batches, hod_name=session['hod_username'], department_name="DEPARTMENT NAME")

# Logout Route
@app.route('/logout')
def logout():
    session.pop('hod_username', None)  # Remove HOD username from session
    session.pop('dept_code', None)  # Remove department code from session
    return redirect(url_for('index'))  # Redirect to login page

# Batches Page Route
@app.route('/batches')
def batches():
    if 'hod_username' not in session:
        return redirect(url_for('index'))  # Redirect to login if not logged in

    batches = list(db.batch.find({}, {'_id': 0, 'batch_id': 1}))
    courses = list(db.courses.find({}, {'_id': 0, 'code': 1, 'title': 1, 'semester': 1}))
    return render_template('batches.html', batches=batches, courses=courses)

# Batches CO Attainment Page Route
@app.route('/batchesco')
def batchesco():
    if 'hod_username' not in session:
        return redirect(url_for('index'))  # Redirect to login if not logged in

    return render_template('batchesco.html')

# Set Threshold Page Route
@app.route('/setth')
def setth():
    if 'hod_username' not in session:
        return redirect(url_for('index'))  # Redirect to login if not logged in

    # Fetch current threshold values from the database
    threshold = db.threshold.find_one({}, {'_id': 0})
    direct_threshold = threshold.get('direct_threshold', 0) if threshold else 0
    indirect_threshold = threshold.get('indirect_threshold', 0) if threshold else 0
    co_attainment = threshold.get('co_attainment', {'level3': 0, 'level2': 0, 'level1': 0}) if threshold else {'level3': 0, 'level2': 0, 'level1': 0}
    return render_template('setth.html', direct_threshold=direct_threshold, indirect_threshold=indirect_threshold, co_attainment=co_attainment)

# Set Threshold 2 Page Route
@app.route('/setth2')
def setth2():
    if 'hod_username' not in session:
        return redirect(url_for('index'))  # Redirect to login if not logged in

    # Fetch current threshold values from the database
    threshold = db.threshold.find_one({}, {'_id': 0})
    direct_threshold = threshold.get('direct_threshold', 0) if threshold else 0
    indirect_threshold = threshold.get('indirect_threshold', 0) if threshold else 0
    co_attainment = threshold.get('co_attainment', {'level3': 0, 'level2': 0, 'level1': 0}) if threshold else {'level3': 0, 'level2': 0, 'level1': 0}
    return render_template('setth2.html', direct_threshold=direct_threshold, indirect_threshold=indirect_threshold, co_attainment=co_attainment)

# Save Threshold Route
@app.route('/save_threshold', methods=['POST'])
def save_threshold():
    if 'hod_username' not in session:
        return redirect(url_for('index'))  # Redirect to login if not logged in

    direct_threshold = request.form.get('direct-threshold')
    indirect_threshold = request.form.get('indirect-threshold')
    level3 = request.form.get('level3')
    level2 = request.form.get('level2')
    level1 = request.form.get('level1')

    if int(direct_threshold) + int(indirect_threshold) != 100:
        flash('The sum of Direct and Indirect Threshold must be exactly 100.', 'error')
    else:
        db.threshold.update_one(
            {},
            {'$set': {
                'direct_threshold': direct_threshold,
                'indirect_threshold': indirect_threshold,
                'co_attainment': {
                    'level3': level3,
                    'level2': level2,
                    'level1': level1
                }
            }},
            upsert=True
        )
        flash('Threshold values and CO Attainment Benchmark saved successfully!', 'success')

    return redirect(url_for('setth'))

# Map Advisor Page Route
@app.route('/mapad')
def mapad():
    if 'hod_username' not in session:
        return redirect(url_for('index'))  # Redirect to login if not logged in

    batches = list(db.batch.find({}, {'_id': 0, 'batch_id': 1, 'adname': 1}))
    modules = list(db.modules.find({}, {'_id': 0, 'module_name': 1, 'mcname': 1}))
    faculties = list(db.faculty.find({'dept_code': session['dept_code']}, {'_id': 1, 'name': 1}))  # Fetch _id and name
    schemas = list(db.schemas.find({}, {'_id': 0, 'schema_name': 1}))
    courses = list(db.courses.find({}, {'_id': 0, 'code': 1, 'title': 1}))
    return render_template('mapad.html', batches=batches, modules=modules, faculties=faculties, schemas=schemas, courses=courses)

# Edit Advisor Route
@app.route('/edit_advisor', methods=['POST'])
def edit_advisor():
    if 'hod_username' not in session:
        return jsonify({"message": "Unauthorized"}), 401  # Unauthorized access

    data = request.json
    batch_id = data.get('batch_id')
    new_advisor_name = data.get('advisor_name')

    # Find the faculty _id based on the selected advisor name
    faculty = db.faculty.find_one({'name': new_advisor_name}, {'_id': 1})
    if not faculty:
        return jsonify({'message': 'Faculty not found'}), 404

    new_advisor_id = faculty['_id']

    # Update in batch collection
    db.batch.update_one({'batch_id': batch_id}, {'$set': {'adname': new_advisor_name, 'advisor_id': new_advisor_id}})

    # Update in advisor collection
    db.advisor.update_one(
        {'batch_id': batch_id},
        {'$set': {'adname': new_advisor_name, 'advisor_id': new_advisor_id}},
        upsert=True
    )

    # Update faculty role to 'advisor'
    db.faculty.update_one({'name': new_advisor_name}, {'$set': {'role': 'advisor'}})

    return jsonify({'message': 'Advisor updated successfully'}), 200

# Delete Batch Route
@app.route('/delete_batch', methods=['POST'])
def delete_batch():
    if 'hod_username' not in session:
        return jsonify({"message": "Unauthorized"}), 401  # Unauthorized access

    data = request.json
    batch_id = data.get('batch_id')

    # Delete from batch collection
    db.batch.delete_one({'batch_id': batch_id})

    # Delete from advisor collection
    db.advisor.delete_one({'batch_id': batch_id})

    return jsonify({'message': 'Batch deleted successfully'}), 200

# Add Batch Route
@app.route('/add_batch', methods=['POST'])
def add_batch():
    if 'hod_username' not in session:
        return jsonify({"message": "Unauthorized"}), 401  # Unauthorized access

    data = request.json
    batch_id = data.get('batch_id')
    advisor_name = data.get('advisor_name')

    # Find the faculty _id based on the selected advisor name
    faculty = db.faculty.find_one({'name': advisor_name}, {'_id': 1})
    if not faculty:
        return jsonify({'message': 'Faculty not found'}), 404

    advisor_id = faculty['_id']

    # Insert into batch collection
    db.batch.insert_one({'batch_id': batch_id, 'adname': advisor_name, 'advisor_id': advisor_id})

    # Insert into advisor collection
    db.advisor.insert_one({'batch_id': batch_id, 'adname': advisor_name, 'advisor_id': advisor_id})

    # Update faculty role to 'advisor'
    db.faculty.update_one({'name': advisor_name}, {'$set': {'role': 'advisor'}})

    return jsonify({'message': 'Batch added successfully'}), 200

# Add Module Route
@app.route('/add_module', methods=['POST'])
def add_module():
    if 'hod_username' not in session:
        return jsonify({"message": "Unauthorized"}), 401  # Unauthorized access

    data = request.json
    module_name = data.get('module_name')
    mc_name = data.get('mc_name')
    schema_name = data.get('schema_name')
    courses = data.get('courses')

    # Update faculty role to 'mc'
    db.faculty.update_one({'name': mc_name}, {'$set': {'role': 'mc'}})

    # Insert into modules collection
    db.modules.insert_one({
        'module_name': module_name,
        'mcname': mc_name,
        'schema_name': schema_name,
        'courses': courses
    })

    return jsonify({'message': 'Module added successfully'}), 200

# Edit Module Coordinator Route
@app.route('/edit_module_coordinator', methods=['POST'])
def edit_module_coordinator():
    if 'hod_username' not in session:
        return jsonify({"message": "Unauthorized"}), 401  # Unauthorized access

    data = request.json
    module_name = data.get('module_name')
    new_mc_name = data.get('mc_name')

    # Update faculty role to 'mc'
    db.faculty.update_one({'name': new_mc_name}, {'$set': {'role': 'mc'}})

    # Update in modules collection
    db.modules.update_one({'module_name': module_name}, {'$set': {'mcname': new_mc_name}})

    return jsonify({'message': 'Module coordinator updated successfully'}), 200

# Delete Module Route
@app.route('/delete_module', methods=['POST'])
def delete_module():
    if 'hod_username' not in session:
        return jsonify({"message": "Unauthorized"}), 401  # Unauthorized access

    data = request.json
    module_name = data.get('module_name')

    # Delete from modules collection
    db.modules.delete_one({'module_name': module_name})

    return jsonify({'message': 'Module deleted successfully'}), 200

# Get Courses by Semester Route
@app.route('/get_courses/<semester>')
def get_courses(semester):
    if 'hod_username' not in session:
        return jsonify({"message": "Unauthorized"}), 401  # Unauthorized access

    courses = list(db.courses.find({'semester': semester}, {'_id': 0, 'code': 1, 'title': 1}))
    return jsonify(courses)

# Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)
