from json import dumps, loads
from turtle import pd
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify,request
from pymongo import MongoClient
from bson.objectid import ObjectId,InvalidId
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import io
import random
import string



admin = Flask(__name__)
admin.secret_key = 'your_secret_key'

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['mini']

# Collections
admin_collection = db['admins']
faculty_collection = db['faculty']
student_collection = db['students']
departments_collection = db['departments']
schema_collection = db['schemas']
course_collection = db['courses']
tool_collection = db['tools']

@admin.route('/')
def index():
    return redirect(url_for('admin_login'))

@admin.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')  # Use request.form for form data
        password = request.form.get('password')

        # Check admin credentials in MongoDB
        admin = admin_collection.find_one({"username": username, "password": password})


        if admin:
            session['admin_id'] = str(admin['_id'])  # Store admin session
            flash("Login successful!", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid credentials!", "error")
    
    return render_template('admin_login.html')



# Generate unique student ID
def generate_student_id(college_code):
    result = db.counters.find_one_and_update(
        {"_id": f"{college_code}_student"},
        {"$inc": {"last_number": 1}},
        upsert=True,
        return_document=True
    )
    next_number = result["last_number"]
    return f"{college_code}-STU-{next_number:03d}"

# Routes
@admin.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        flash("Please login first!", "error")
        return redirect(url_for('admin_login'))
    print(session.get('admin_id'))  # Check if session is being set correctly
    admin_data = admin_collection.find_one({"_id": ObjectId(session['admin_id'])})
    clg_name = admin_data.get("clg_name", "")
    univ_name = admin_data.get("univ_name", "")
    return render_template('admin1.html',college_name=clg_name, university_name=univ_name)

# Logout route
@admin.route('/logout')
def logout():
    session.pop('admin_id', None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('admin_login'))

@admin.route('/add_faculty', methods=['GET', 'POST'])
def add_faculty():
    if 'admin_id' not in session:
        flash("Please login first!", "error")
        return redirect(url_for('admin_login'))
    
    admin_data = admin_collection.find_one({"_id": ObjectId(session['admin_id'])})

    clg_id = admin_data.get("clg_id", "")
    univ_code = admin_data.get("univ_code", "")
    clg_name = admin_data.get("clg_name", "")
    univ_name = admin_data.get("univ_name", "")

    if request.method == 'POST':
        if 'csv-file' in request.files:
            file = request.files['csv-file']
            if file.filename.endswith('.csv'):
                stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                csv_reader = csv.DictReader(stream)
                for row in csv_reader:
                    pen_no = row.get('pen_no', '').strip()
                    name = row.get('name', '').strip()
                    dept_code = row.get('dept_code', '').strip()
                    designation = row.get('designation', '').strip()

                # Check if pen_no exists and isn't empty
                    if pen_no:
                        existing = faculty_collection.find_one({
                            'pen_no': pen_no,
                            'clg_id': clg_id,
                            'univ_code': univ_code
                        })

                        if not existing:
                            faculty_collection.insert_one({
                                "pen_no": pen_no,
                                "name": name,
                                "dept_code": dept_code,
                                "designation": designation,
                                "univ_code": univ_code,
                                "clg_id": clg_id,
                                "password": "",
                                "admin_id": session['admin_id']
                            })
                        else:
                            print(f"Duplicate entry found for pen_no: {pen_no}")
                    else:
                        print("Skipping row with missing pen_no")

                        
                flash('Faculty data uploaded successfully!', 'success')
        else:
            pen_no = request.form["pen_no"]
            name = request.form["name"]
            dept_code = request.form["dept_code"]
            designation = request.form["designation"]
            password = request.form["password"]

            faculty_collection.insert_one({
                "pen_no": pen_no,
                "name": name,
                "dept_code": dept_code,
                "designation": designation,
                "password": password,
                "clg_id": clg_id,  # Ensure only admin's college ID is used
                "univ_code": univ_code,
                "admin_id": session['admin_id']
            })
            
    faculties = list(db.faculty.find({}))  # Fetch all faculty documents
    for faculty in faculties:
        faculty['_id'] = str(faculty['_id']) 

    return render_template('admin2.html', faculties=faculties, college_name=clg_name, university_name=univ_name, clg_id=clg_id, univ_code=univ_code)



@admin.route('/get_faculty_list',methods=['POST'])
def get_faculty_data():
    faculties = list(db.faculty.find({"admin_id": session['admin_id']}, {"_id": 0}))
    return (faculties)

from flask import request, jsonify

@admin.route('/submit_faculty_data', methods=['POST'])
def submit_faculty_data():
    admin_data = admin_collection.find_one({"_id": ObjectId(session['admin_id'])})

    # Extract college and university details
    clg_id = admin_data.get("clg_id", "")
    univ_code = admin_data.get("univ_code", "")
    try:
        # Ensure we are receiving JSON data
        if request.content_type != 'application/json':
            return jsonify({"error": "Unsupported Media Type"}), 415
        
        data = request.json  # Extract JSON payload
        pen_no = data.get("pen_no")
        name = data.get("name")
        dept_code = data.get("dept_code")
        designation = data.get("designation")

        # Check if faculty already exists
        existing_faculty = db.faculty.find_one({"pen_no": pen_no, "clg_id": clg_id, "univ_code": univ_code})
        if existing_faculty:
            return jsonify({"error": "Faculty already exists"}), 400

        # Insert new faculty
        db.faculty.insert_one({
            "pen_no": pen_no,
            "clg_id":clg_id,
            "univ_code":univ_code,
            "name": name,
            "dept_code": dept_code,
            "designation": designation,
            "password": "",  # Default empty password
            "admin_id": session['admin_id']  # Link to admin
        })
        
        return jsonify({"message": "Faculty added successfully!"}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin.route('/search_faculty', methods=['GET'])
def search_faculty():
    if 'admin_id' not in session:
        flash("Please login first!", "error")
        return redirect(url_for('admin_login'))

    admin_data = admin_collection.find_one({"_id": ObjectId(session['admin_id'])})
    clg_id = admin_data.get("clg_id", "")

    department_code = request.args.get('department_code', '').strip().lower()
    pen_no = request.args.get('pen_no', '').strip()

    query = {"clg_id": clg_id}  # Filter by admin's college
    if department_code:
        query["dept_code"] = {"$regex": f"^{department_code}$", "$options": "i"}
    if pen_no:
        query["pen_no"] = pen_no

    faculties = list(faculty_collection.find(query, {"_id": 0, "password": 0}))

    return jsonify(faculties)  # Send JSON response

@admin.route('/generate_password/<faculty_id>', methods=['POST'])
def generate_password(faculty_id):
    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    result = faculty_collection.update_one(
        {"_id": ObjectId(faculty_id)},
        {"$set": {"password": new_password}}
    )
    if result.modified_count == 1:
        return jsonify({"success": True, "password": new_password})
    return jsonify({"error": "Failed to update password"}), 400

def generate_random_password(length=8):
    """Generate a random password with uppercase, lowercase, digits, and special characters."""
    characters = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(characters) for _ in range(length))  

@admin.route('/generate_all_passwords', methods=['POST'])
def generate_all_passwords():
    try:
        faculty_collection = db["faculty"]  # Ensure you're using the correct collection

        faculty_members = faculty_collection.find()
        for faculty in faculty_members:
            print(faculty)  # Debugging: Print each document

            # Check if 'faculty_id' exists, otherwise use '_id'
            faculty_id = faculty.get('faculty_id', faculty.get('_id'))
            if not faculty_id:
                continue  # Skip if there's no valid ID

            new_password = generate_random_password()  # Function to generate a password
            
            # If '_id' is an ObjectId, ensure it's properly used in the query
            faculty_collection.update_one(
                {'_id': ObjectId(faculty_id) if isinstance(faculty_id, str) else faculty_id},
                {'$set': {'password': new_password}}
            )

        return jsonify({"message": "Passwords generated successfully"}), 200
    except Exception as e:
        print("Error:", str(e))  # Log the error
        return jsonify({"error": str(e)}), 500

@admin.route('/delete_faculty/<faculty_id>', methods=['DELETE'])
def delete_faculty(faculty_id):
    faculty = db.faculty.find_one({"_id": ObjectId(faculty_id)})
    if not faculty:
        return jsonify({"error": "Faculty not found"}), 404
    
    db.faculty.delete_one({"_id": ObjectId(faculty_id)})
    return jsonify({"message": "Faculty deleted successfully"}), 200
    
@admin.route('/get_faculty/<faculty_id>', methods=['GET'])
def get_faculty(faculty_id):
    try:
        faculty = db.faculty.find_one({"_id": ObjectId(faculty_id)})
        if not faculty:
            return jsonify({"error": "Faculty not found"}), 404

        # Convert ObjectId to string before returning
        faculty['_id'] = str(faculty['_id'])
        return jsonify(faculty)
    except Exception as e:
        print("Error fetching faculty:", e)  # Check server logs
        return jsonify({"error": "An error occurred while fetching faculty details"}), 500

# Route to update faculty details
@admin.route('/update_faculty/<faculty_id>', methods=['POST'])
def update_faculty(faculty_id):
    data = request.get_json()
    updated_data = {
        "pen_no": data['pen_no'],
        "name": data['name'],
        "dept_code": data['dept_code'],
        "designation": data['designation']
    }

    result = db.faculty.update_one({"_id": ObjectId(faculty_id)}, {"$set": updated_data})

    if result.modified_count == 1:
        return jsonify({"message": "Faculty details updated successfully!"}), 200
    else:
        return jsonify({"error": "Failed to update faculty details."}), 400


@admin.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'admin_id' not in session:
        flash("Please login first!", "error")
        return redirect(url_for('admin_login'))

    admin_id = session['admin_id']
    admin_data = admin_collection.find_one({"_id": ObjectId(admin_id)})

    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['password']  # Directly take password

        # Check if username is already taken (except for current admin)
        existing_user = admin_collection.find_one({"username": username, "_id": {"$ne": ObjectId(admin_id)}})
        if existing_user:
            flash("Username already taken. Choose a different one.", "error")
            return redirect(url_for('edit_profile'))

        update_data = {"username": username}
        if new_password:  # Only update password if provided
            update_data["password"] = new_password  # Store as plain text

        admin_collection.update_one({"_id": ObjectId(admin_id)}, {"$set": update_data})
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('edit_profile'))

    return render_template('edit_profile.html', admin=admin_data)

@admin.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if 'admin_id' not in session:
        flash("Please login first!", "error")
        return redirect(url_for('admin_login'))
    
    admin_data = admin_collection.find_one({"_id": ObjectId(session['admin_id'])})

    clg_id = admin_data.get("clg_id", "")
    univ_code = admin_data.get("univ_code", "")
    clg_name = admin_data.get("clg_name", "")
    univ_name = admin_data.get("univ_name", "")

    if request.method == 'POST':
        if 'csv-file' in request.files:
            file = request.files['csv-file']
            if file.filename.endswith('.csv'):
                stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                csv_reader = csv.DictReader(stream)
                for row in csv_reader:
                    univ_no= row.get("univ_no", "").strip()
                    name= row.get("name", "").strip()
                    dept_code=row.get("dept_code","").strip()
                    reg_no= row.get("reg_no", "").strip()
                    batch= row.get("batch", "").strip()
                    

                # Check if pen_no exists and isn't empty
                    if reg_no:
                        existing = student_collection.find_one({
                            'reg_no': reg_no,
                            'clg_id': clg_id,
                            'univ_code': univ_code
                        })

                        if not existing:
                            student_collection.insert_one({
                                "reg_no": reg_no,
                                "name": name,
                                "dept_code": dept_code,
                                "batch": batch,
                                "univ_no":univ_no,
                                "univ_code": univ_code,
                                "clg_id": clg_id,
                                "admin_id": session['admin_id']
                            })
                        else:
                            print(f"Duplicate entry found for reg_no: {reg_no}")
                    else:
                        print("Skipping row with missing reg_no")

                        
                flash('student data uploaded successfully!', 'success')
        else:
            univ_no = request.form.get("univ_no", "").strip()
            name = request.form.get("name", "").strip()
            dept_code = request.form.get("dept_code", "").strip()
            batch = request.form.get("batch", "").strip()
            reg_no = request.form.get("reg_no", "").strip()


            student_collection.insert_one({
                "reg_no": reg_no,
                "name": name,
                "dept_code": dept_code,
                "batch": batch,
                "univ_no":univ_no,
                "univ_code": univ_code,
                "clg_id": clg_id,
                "admin_id": session['admin_id']
            })
            
    students = list(db.students.find({}))  # Fetch all faculty documents
    for student in students:
        student['_id'] = str(student['_id']) 

    return render_template('admin3.html', students=students, college_name=clg_name, university_name=univ_name, clg_id=clg_id, univ_code=univ_code)

@admin.route('/submit_student_data', methods=['POST'])
def submit_student_data():
    admin_data = admin_collection.find_one({"_id": ObjectId(session['admin_id'])})

    # Extract college and university details
    clg_id = admin_data.get("clg_id", "")
    univ_code = admin_data.get("univ_code", "")

    try:
        # Ensure we are receiving JSON data
        if request.content_type != 'application/json':
            return jsonify({"error": "Unsupported Media Type"}), 415

        data = request.json  # Extract JSON payload
        reg_no = data.get("reg_no")
        name = data.get("name")
        dept_code = data.get("dept_code")
        batch = data.get("batch")
        univ_no = data.get("univ_no")

        # Check if student already exists
        existing_student = db.students.find_one({
            "reg_no": reg_no, 
            "clg_id": clg_id, 
            "univ_code": univ_code
        })
        if existing_student:
            return jsonify({"error": "Student already exists"}), 400

        # Insert new student
        db.students.insert_one({
            "reg_no": reg_no,
            "clg_id": clg_id,
            "univ_code": univ_code,
            "name": name,
            "dept_code": dept_code,
            "batch": batch,
            "univ_no": univ_no,
            "password": "",  # Default empty password
            "admin_id": session['admin_id']  # Link to admin
        })

        return jsonify({"message": "Student added successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Search Students
@admin.route('/search_students', methods=['GET'])
def search_students():
    if 'admin_id' not in session:
        return jsonify({"error": "Please login first!"}), 401

    admin_data = admin_collection.find_one({"_id": ObjectId(session['admin_id'])})
    clg_id = admin_data.get("clg_id", "")

    batch = request.args.get("batch", "").strip()
    dept_code = request.args.get("dept_code", "").strip()

    query = {"clg_id": clg_id}
    if batch:
        query["batch"] = batch
    if dept_code:
        query["dept_code"] = dept_code

    students = list(student_collection.find(query, {"_id": 0}))
    return jsonify(students), 200

# Delete Student
@admin.route('/delete_student/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    if 'admin_id' not in session:
        return jsonify({"error": "Please login first!"}), 401

    result = student_collection.delete_one({"_id": ObjectId(student_id)})
    if result.deleted_count == 1:
        return jsonify({"message": "Student deleted successfully!"}), 200
    else:
        return jsonify({"error": "Student not found!"}), 404

@admin.route('/get_student/<student_id>', methods=['GET'])
def get_student(student_id):
    try:
        student = student_collection.find_one({"_id": ObjectId(student_id)})
        if not student:
            return jsonify({"error": "Student not found"}), 404

        student['_id'] = str(student['_id'])
        return jsonify(student)
    except InvalidId:
        return jsonify({"error": "Invalid ID format"}), 400
    except Exception as e:
        print("Error fetching student:", e)
        return jsonify({"error": "An error occurred while fetching student details"}), 500

@admin.route('/get_student_list', methods=['POST'])
def get_student_data():
    students = list(db.student.find({"admin_id": session['admin_id']}, {"_id": 0}))
    return jsonify(students)  # Use jsonify to return valid JSON response

# Update Student
@admin.route('/update_student/<student_id>', methods=['POST'])
def update_student(student_id):
    if 'admin_id' not in session:
        return jsonify({"error": "Please login first!"}), 401

    data = request.get_json()
    updated_data = {
        "name": data.get("name"),
        "reg_no": data.get("reg_no"),
        "batch": data.get("batch"),
        "univ_no": data.get("univ_no"),
        "dept_code": data.get("dept_code")
    }

    result = student_collection.update_one({"_id": ObjectId(student_id)}, {"$set": updated_data})
    if result.modified_count == 1:
        return jsonify({"message": "Student updated successfully!"}), 200
    else:
        return jsonify({"error": "Failed to update student!"}), 400
    
# Route to Add Department
@admin.route('/add_department', methods=['GET', 'POST'])
def add_department():
    admin_data = admin_collection.find_one({"_id": ObjectId(session['admin_id'])})

    clg_name = admin_data.get("clg_name", "")
    univ_name = admin_data.get("univ_name", "")
    if request.method == 'POST':
        dept_name = request.form.get('dept_name')
        dept_code = request.form.get('dept_code')
        hod_username = request.form.get('hod_username')
        hod_password = request.form.get('hod_password')

        # Insert department details into MongoDB
        departments_collection.insert_one({
            'dept_name': dept_name,
            'dept_code': dept_code,
            'hod_username': hod_username,
            'hod_password': hod_password
        })

        flash('Department added successfully!')
        return redirect(url_for('add_department'))

    # Convert ObjectId to string for JSON serialization
    departments = list(departments_collection.find())
    for dept in departments:
        dept['_id'] = str(dept['_id'])

    return render_template('admin6.html', college_name=clg_name, university_name=univ_name, departments=departments)

# Route to Edit Department

@admin.route('/edit_department/<dept_id>', methods=['POST'])
def edit_department(dept_id):
    updated_data = request.get_json()
    departments_collection.update_one(
        {'_id': ObjectId(dept_id)},
        {'$set': updated_data}
    )
    return jsonify({'success': True, 'message': 'Department updated successfully!'})


# Route to Delete Department
@admin.route('/delete_department/<dept_id>')
def delete_department(dept_id):
    departments_collection.delete_one({'_id': ObjectId(dept_id)})
    flash('Department deleted successfully!')
    return redirect(url_for('add_department'))
    
@admin.route('/add_schema', methods=['GET', 'POST'])
def add_schema():
    if 'admin_id' not in session:
        flash("Please login first!", "error")
        return redirect(url_for('admin_login'))
    
    admin_data = admin_collection.find_one({"_id": ObjectId(session['admin_id'])})

    clg_id = admin_data.get("clg_id", "")
    univ_code = admin_data.get("univ_code", "")
    clg_name = admin_data.get("clg_name", "")
    univ_name = admin_data.get("univ_name", "")
    
    if request.method == 'POST':
        schema_name= request.form.get('schema_name','').strip()
        
        schema_collection.insert_one({
            "schema_name": schema_name,
            "univ_code": univ_code,
            "clg_id": clg_id,
            "admin_id": session['admin_id']
        })
        flash('Schema added successfully!', 'success')
        return redirect(url_for('add_schema'))

    schemas = list(schema_collection.find({"admin_id": session['admin_id']}))
    return render_template('admin4.html', schemas=schemas,college_name=clg_name,university_name=univ_name)

# Route to upload courses using CSV
@admin.route('/upload_courses', methods=['POST'])
def upload_courses():
    if 'admin_id' not in session:
        flash("Please login first!", "error")
        return redirect(url_for('admin_login'))

    admin_data = admin_collection.find_one({"_id": ObjectId(session['admin_id'])})
    clg_id = admin_data.get("clg_id", "")
    univ_code = admin_data.get("univ_code", "")

    if 'csv_file' in request.files:
        file = request.files['csv_file']
        if file.filename.endswith('.csv'):
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)

            for row in csv_reader:
                course_code = row.get('course_code', '').strip()
                course_title = row.get('course_title', '').strip()
                course_type = row.get('course_type', '').strip()
                semester = row.get('semester', '').strip()
                dept_code = row.get('dept_code', '').strip()
                schema_name = row.get('schema_name', '').strip()

                # Check if essential data exists
                if not course_code or not schema_name:
                    print(f"Skipping row with missing course_code or schema_name: {row}")
                    continue  # Skip this row if essential data is missing

                # Check if the schema exists
                existing_schema = schema_collection.find_one({'schema_name': schema_name})
                if not existing_schema:
                    print(f"Schema '{schema_name}' does not exist. Skipping course {course_code}.")
                    continue  # Skip this course if schema is not found

                # Check if the course already exists
                existing_course = course_collection.find_one({
                    'schema_name': schema_name,
                    'course_code': course_code,
                    'semester': semester
                })

                if not existing_course:
                    course_collection.insert_one({
                        "schema_name": schema_name,
                        "details": {
                            "clg_id": clg_id,
                            "univ_code": univ_code
                        },
                        "course_code": course_code,
                        "course_title": course_title,
                        "course_type": course_type,
                        "dept_code": dept_code,
                        "semester": semester,
                        "admin_id": session['admin_id']
                    })
                else:
                    print(f"Duplicate entry found for course_code: {course_code} in semester: {semester}")

            flash('Courses uploaded successfully!', 'success')
            return redirect(url_for('add_course'))
        else:
            flash("Invalid file format. Please upload a CSV file.", "error")
            return redirect(url_for('add_course'))
    else:
        flash("No CSV file found in the request.", "error")
        return redirect(url_for('upload_courses'))
    

@admin.route('/add_course', methods=['POST'])
def add_course():
    if 'admin_id' not in session:
        flash("Please login first!", "error")
        return redirect(url_for('admin_login'))
    
    admin_data = admin_collection.find_one({"_id": ObjectId(session['admin_id'])})
    clg_id = admin_data.get("clg_id", "")
    univ_code = admin_data.get("univ_code", "")
    
    schema_id = request.form.get('schema_id', '').strip()
    if schema_id:
        schema_id = ObjectId(schema_id)

    # Fetch schema_name from the schemas table
    schema = schema_collection.find_one({"_id": schema_id})
    if not schema:
        flash("Schema not found!", "error")
        return redirect(url_for('add_schema'))

    schema_name = schema["schema_name"]

    course_code = request.form.get('course_code', '').strip()
    course_title = request.form.get('course_title', '').strip()
    course_type = request.form.get('course_type', '').strip()
    dept_code = request.form.get('dept_code', '').strip()
    semester = int(request.form.get('semester', '').strip())

    # Prevent duplicate insertion
    existing_course = course_collection.find_one({
        "course_code": course_code,
        "schema_id": schema_id
    })

    if existing_course:
        flash('Course already exists for this schema!', 'error')
        return redirect(url_for('add_schema'))

    # Insert the course with schema_name
    course_collection.insert_one({
        "schema_name": schema_name,  # Store schema_name
        "details": {
            "clg_id": clg_id,
            "univ_code": univ_code
        },
        "course_code": course_code,
        "course_title": course_title,
        "course_type": course_type,
        "dept_code": dept_code,
        "semester": semester,
        "admin_id": session['admin_id']
    })

    flash('Course added successfully!', 'success')
    return redirect(url_for('add_schema'))

@admin.route('/search_courses', methods=['POST'])
def search_courses():
    try:
        data = request.get_json()
        print("Received data:", data)  # Debug incoming data

        schema_name = data.get('schema_name')
        semester = str(data.get('semester'))

        if not schema_name or semester is None:
            return jsonify({"error": "Schema name and semester are required."}), 400

        # Fetch courses directly based on schema_name and semester
        courses = list(course_collection.find({'schema_name': schema_name, 'semester': semester}))

        print("Found courses:", courses)  # Debug the output from MongoDB

        # Convert ObjectId to string
        for course in courses:
            course['_id'] = str(course['_id'])

        return jsonify(courses)
    except Exception as e:
        print(f"Error fetching courses: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@admin.route('/get_courses/<schema_name>/<int:semester>', methods=['GET'])
def get_courses(schema_name, semester):
    try:
        courses = list(course_collection.find({"schema_name": schema_name, "semester": semester}))

        # Convert ObjectId to string and include schema_name
        for course in courses:
            course["_id"] = str(course["_id"])
            course["schema_name"] = course.get("schema_name", "Unknown Schema")  # Include schema_name

        return jsonify({"courses": courses})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@admin.route('/delete_course/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    if 'admin_id' not in session:
        return {"status": "error", "message": "Please login first!"}, 401

    # Attempt to delete the course
    result = course_collection.delete_one({
        '_id': ObjectId(course_id),
        'admin_id': session['admin_id']
    })

    if result.deleted_count > 0:
        return {"status": "success", "message": "Course deleted successfully!"}
    else:
        return {"status": "error", "message": "Course not found or unauthorized access"}, 404

@admin.route('/get_course/<course_id>', methods=['GET'])
def get_course(course_id):
    try:
        course = db.courses.find_one({"_id": ObjectId(course_id)})
        if course:
            # Return course data as JSON
            return jsonify({
                "_id": str(course["_id"]),  # Convert ObjectId to string
                "course_code": course["course_code"],
                "course_title": course["course_title"],  # Ensure this matches the frontend
                "course_type": course["course_type"],
                "dept_code": course["dept_code"],
                "semester": course["semester"],
                "schema_name": course["schema_name"],  # Optional field
            })
        else:
            return jsonify({"error": "Course not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Route to update course details
@admin.route('/update_course/<course_id>', methods=['POST'])
def update_course(course_id):
    try:
        data = request.json
        schema_name = data.get("schema_name")

        existing_schema = schema_collection.find_one({'schema_name': schema_name})
        if not existing_schema:
            return jsonify({"error": "The provided schema does not exist."}), 400
        updated_data = {
            "course_code": data.get("course_code"),
            "course_title": data.get("course_name"),
            "course_type": data.get("course_type"),
            "dept_code": data.get("dept_code"),
            "semester": data.get("semester"),
            "schema_name": schema_name  # Store validated schema_name
        }

        result = course_collection.update_one(
            {"_id": ObjectId(course_id)},
            {"$set": updated_data}
        )

        if result.modified_count > 0:
            return jsonify({"message": "Course updated successfully!"})
        else:
            return jsonify({"error": "No changes made or course not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@admin.route('/add_tool', methods=['GET', 'POST'])
def add_tool():
    if 'admin_id' not in session:
        flash("Please login first!", "error")
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        schema_id = request.form['schema_id']  # Ensure schema_id is captured
        tool_name = request.form['tool_name']
        tool_description = request.form['tool_description']

        # Check if schema exists
        schema = schema_collection.find_one({"_id": ObjectId(schema_id)})
        if not schema:
            flash("Selected schema does not exist!", "error")
            return redirect(url_for('add_tool'))

        # Insert tool with schema reference
        tool_collection.insert_one({
            "tool_name": tool_name,
            "tool_description": tool_description,
            "schema_id": ObjectId(schema_id),
            "schema_name": schema["schema_name"],  # Store schema name for easy access
            "admin_id": session['admin_id']
        })
        flash('Tool added successfully!', 'success')
        return redirect(url_for('add_tool'))

    # Fetch available schemas
    schemas = list(schema_collection.find({}, {"_id": 1, "schema_name": 1}))
    tools = list(tool_collection.find({"admin_id": session['admin_id']}))
    return render_template('admin7.html', schemas=schemas, tools=tools)

@admin.route('/get_tools/<schema_id>')
def get_tools(schema_id):
    try:
        schema_id = ObjectId(schema_id)
        tools = list(tool_collection.find({"schema_id": schema_id}, {"_id": 1,"schema_name":1, "tool_name": 1, "tool_description": 1}))

        for tool in tools:
            tool["_id"] = str(tool["_id"])  # Convert ObjectId to string for JSON serialization

        return jsonify(tools)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@admin.route('/get_evaluation_tool/<tool_id>', methods=['GET'])
def get_evaluation_tool(tool_id):
    try:
        object_id = ObjectId(tool_id)  # Ensure tool_id is a valid ObjectId
    except InvalidId:
        return jsonify({"error": "Invalid Tool ID format"}), 400  # Return 400 for invalid ID

    tool = db.tools.find_one({"_id": object_id})  # Ensure correct collection name
    if tool:
        # Convert ObjectId fields to string
        tool['_id'] = str(tool['_id'])
        tool['schema_id'] = str(tool['schema_id'])  # Convert any ObjectId fields
        return jsonify(tool)
    
    return jsonify({"error": "Tool not found"}), 404  

@admin.route('/update_evaluation_tool/<tool_id>', methods=['POST'])
def update_evaluation_tool(tool_id):
    try:
        object_id = ObjectId(tool_id)  # Convert tool_id to ObjectId
    except InvalidId:
        return jsonify({"error": "Invalid ObjectId format"}), 400

    data = request.json
    print(data)
    updated_data = {
        "tool_name": data.get("tool_name"),
        "tool_description": data.get("tool_description"),
    }
    
    result = db.tools.update_one({"_id": object_id}, {"$set": updated_data})

    if result.modified_count > 0:
        return jsonify({"message": "Tool updated successfully"}), 200
    return jsonify({"error": "Failed to update tool"}), 400


    
@admin.route('/delete_evaluation_tool/<tool_id>', methods=['DELETE'])
def delete_evaluation_tool(tool_id):
    try:
        object_id = ObjectId(tool_id)  # Convert tool_id to ObjectId
    except InvalidId:
        return jsonify({"error": "Invalid ObjectId format"}), 400

    result = db.tools.delete_one({"_id": object_id})

    if result.deleted_count > 0:
        return jsonify({"message": "Tool deleted successfully"}), 200
    return jsonify({"error": "Failed to delete tool"}), 400

@admin.route('/view_batches')
def view_batches():
    batches = student_collection.distinct("batch")
    return render_template('view_batches.html', batches=batches)

if __name__ == '__main__':
    admin.run(debug=True)
    
    get_faculty