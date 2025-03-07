import csv
import datetime
import os
from cv2 import threshold
import pandas as pd
import uuid
import bcrypt
from bson import ObjectId
from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/mini"
mongo = PyMongo(app)
app.secret_key = 'your_secret_key'  # Session Management

# MongoDB Connection
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
course_mapping_collection = db['course_mapping']
co_collection = db["course_outcomes"]
session_collection = db["sessions"]
matrix_collection = db["co_po_matrix"]
tool_config_collection = db["tool_config"]
marks_collection = db['student_marks']
co_achievement_collection = db["internal_co"]
question_collection =db["questions"]
achievements_collection = db["co_achievements"]
thresholds_collection = db["thresholds"]


@app.route('/')
def index():
    return redirect(url_for('faculty_login'))

@app.route('/faculty_login', methods=['GET'])
def faculty_login_page():
    return render_template('login.html')

# 📌 Faculty Login API
@app.route('/faculty_login', methods=['POST'])
def faculty_login():
    data = request.json
    pen_no = data.get('pen_no')
    password = data.get('password')

    faculty = faculty_collection.find_one({"pen_no": pen_no})
    if not faculty:
        return jsonify({"success": False, "message": "Invalid Credentials!"}), 401

    stored_hashed_password = faculty["password"].encode("utf-8")
    entered_password = password.encode("utf-8")

    if not bcrypt.checkpw(entered_password, stored_hashed_password):
        return jsonify({"success": False, "message": "Invalid Credentials!"}), 401

    session_id = str(uuid.uuid4())

    # Extract advisor_batches from faculty's role field
    advisor_batches = faculty.get('role', {}).get('advisor', [])  # Default to empty list if missing
    is_mc = faculty.get('role', {}).get('mc', False)  # Default to False if missing

    # Store faculty details in session
    session['session_id'] = session_id
    session['faculty_id'] = str(faculty['_id'])  # Convert ObjectId to string
    session['pen_no'] = faculty['pen_no']
    session['name'] = faculty['name']
    session['dept_code'] = faculty['dept_code']
    session['role'] = "FACULTY"
    session['advisor_batches'] = advisor_batches 
    session['is_mc'] = is_mc 

    # Save session details in a separate collection
    session_collection.insert_one({
        "session_id": session_id,
        "faculty_id": str(faculty['_id']),  # Store faculty_id in session DB
        "pen_no": pen_no,
        "login_time": datetime.datetime.utcnow(),
        "active": True
    })

    print("Session Data After Login:", session)  # Debugging

    return jsonify({
        "success": True,
        "message": "Login successful",
        "session_id": session_id,
        "redirect_url": url_for('faculty_dashboard')
    })

# 📌 Faculty Dashboard Route
@app.route('/faculty_dashboard')
def faculty_dashboard():
    if 'pen_no' not in session:
        return redirect(url_for('faculty_login_page'))
    
    print("Session Data:", session) 
    # Fetch faculty details
    faculty_info = {
        "pen_no": session['pen_no'],
        "name": session['name'],
        "dept_code": session['dept_code'],
        "advisor_batches": session.get('advisor_batches', []),
        "is_mc": session.get('is_mc', False)
    }
    
    print(faculty_info["is_mc"])
    # Fetch assigned teaching batches
    assigned_courses = list(course_mapping_collection.find(
        {"pen_no": session['pen_no']}, {"_id": 0, "course_title": 1, "batch": 1}
    ))

    print("Assigned Courses:", assigned_courses)  # Debugging

    return render_template('faculty_dashboard.html',
                           faculty=faculty_info,
                           teaching_batches=assigned_courses,
                           is_advisor=len(faculty_info["advisor_batches"]) > 0)  # Pass advisor status
    
@app.route('/mc')
def mc_dashboard():
    """Render the MC dashboard with CO requests."""
    co_requests = list(db.course_outcomes.find({'is_approved': False}))  
    print("CO Requests Fetched:", co_requests)  # Debugging
    return render_template('mc.html', requests=co_requests)

@app.route('/approve_co', methods=['POST'])
def approve_co():
    """Approve a CO request, update DB, and notify faculty."""
    data = request.json
    co_id = data.get('co_id')
    

    if co_id:
        db.course_outcomes.update_one(
            {"_id": ObjectId(co_id)},
            {"$set": {"is_approved": True}}
        )
        return jsonify({"message": "CO approved successfully", "status": "approved"})
    
    return jsonify({"error": "Invalid request"}), 400

@app.route('/reject_co', methods=['POST'])
def reject_co():
    """Reject a CO request and notify the faculty."""
    data = request.json
    co_id = data.get('co_id')

    if co_id:
        db.course_outcome.delete_one({"_id": ObjectId(co_id)})  # Remove the rejected CO request
        return jsonify({"message": "CO request rejected successfully", "status": "rejected"})

    return jsonify({"error": "Invalid request"}), 400

@app.route('/edit_co_threshold', methods=['POST'])
def edit_co_threshold():
    """Edit only the CO weightage and update in the database."""
    data = request.json
    co_id = data.get('co_id')
    new_threshold = data.get('threshold')

    if co_id and new_threshold and new_threshold.isdigit():
        db.course_outcomes.update_one(
            {"_id": ObjectId(co_id)},
            {"$set": {"threshold": int(new_threshold)}}
        )
        return jsonify({"message": "Threshold updated successfully", "status": "edited"})

    return jsonify({"error": "Invalid request"}), 400

@app.route('/threshold')
def threshold_page():
    """Render the threshold page"""
    return render_template("threshold.html")

@app.route("/threshold", methods=["POST"])
def save_threshold():
    try:
        internal_th = request.form.get("internalThreshold")
        external_th = request.form.get("externalThreshold")
        external_grade = request.form.get("external")

        if not internal_th or not external_th or not external_grade:
            return jsonify({"error": "Missing required fields"}), 400

        internal_th = int(internal_th)
        external_th = int(external_th)

        if internal_th + external_th != 100:
            return jsonify({"error": "Threshold sum must be 100"}), 400

        # Fetch faculty details dynamically
        faculty_pen_no = session.get("pen_no")  # Assuming session stores logged-in faculty
        faculty = db["faculty"].find_one({"pen_no": faculty_pen_no})

        if not faculty:
            return jsonify({"error": "Faculty not found"}), 400

        # Store threshold data
        insert_result = db.thresholds.insert_one({
            "internal_th": internal_th,
            "external_th": external_th,
            "external_grade": external_grade,
            "pen_no": faculty_pen_no,
            "course": faculty["course"],
            "dept_code": faculty["dept_code"]
        })

        return jsonify({"success": "Threshold saved successfully!", "id": str(insert_result.inserted_id)}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/api/faculty")
def get_faculty():
    if "pen_no" not in session:
        return jsonify({"error": "Unauthorized access"}), 401

    pen_no = session["pen_no"]

    # 🔹 Fetch faculty details
    faculty = faculty_collection.find_one({"pen_no": pen_no}, {"_id": 0, "name": 1, "role": 1})

    if not faculty:
        return jsonify({"error": "Faculty not found"}), 404

    faculty_name = faculty.get("name", "Unknown")
    roles = faculty.get("role", {})
    is_advisor = "advisor" in roles

    # 🔹 Fetch courses the faculty is teaching
    teaching_courses = list(course_mapping_collection.find(
        {"pen_no": pen_no},
        {"_id": 0, "course_title": 1, "batch": 1}
    ))

    # 🔹 Fetch advising batches
    advising_batches = roles.get("advisor", [])

    return jsonify({
        "pen_no": pen_no,
        "name": faculty_name,
        "roles": list(roles.keys()),  # Extract role names
        "is_advisor": is_advisor,
        "teaching_batches": [{"Course": course["course_title"], "Batch": course["batch"]} for course in teaching_courses],
        "advising_batches": [{"Semester": semester} for semester in advising_batches]
    })

@app.route('/faculty_change_password_page', methods=['GET'])
def faculty_change_password_page():
    if 'pen_no' not in session:
        return redirect(url_for('faculty_login_page'))
    return render_template('faculty_change_password.html')

@app.route('/faculty_change_password', methods=['POST'])
def faculty_change_password():
    if 'pen_no' not in session:
        return jsonify({"success": False, "message": "Unauthorized. Please log in."}), 401

    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({"success": False, "message": "Both current and new passwords are required!"}), 400

    pen_no = session['pen_no']
    faculty = faculty_collection.find_one({"pen_no": pen_no})

    if not faculty:
        return jsonify({"success": False, "message": "Faculty not found!"}), 404

    # 🔹 Compare entered password with stored hashed password
    stored_hashed_password = faculty["password"].encode("utf-8")
    entered_password = current_password.encode("utf-8")

    if not bcrypt.checkpw(entered_password, stored_hashed_password):
        return jsonify({"success": False, "message": "Incorrect current password!"}), 401

    # 🔹 Hash the new password before saving
    hashed_new_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())

    # 🔹 Update password in MongoDB
    faculty_collection.update_one({"pen_no": pen_no}, {"$set": {"password": hashed_new_password.decode("utf-8")}})

    return jsonify({"success": True, "message": "Password changed successfully!"})

# 📌 Faculty Logout
@app.route('/faculty_logout')
def faculty_logout():
    session.clear()
    return redirect(url_for('faculty_login'))

@app.route('/view_batch/<semester>')
def view_batch(semester):
    if 'pen_no' not in session or session['role'] != 'FACULTY':
        return redirect(url_for('faculty_login_page'))

    pen_no = session['pen_no']

    # 🔹 Fetch batch details for the given semester & faculty
    batch_details = list(course_mapping_collection.find(
        {"pen_no": pen_no, "batch": semester},
        {"_id": 0, "course_title": 1, "batch": 1, "dept_code": 1}
    ))

    # If no batch found, redirect back
    if not batch_details:
        flash("No assigned batch found for this semester!", "error")
        return redirect(url_for('faculty_dashboard'))  

    # 🔹 Fetch course details correctly
    course_titles = [batch["course_title"] for batch in batch_details]
    courses = list(course_collection.find(
        {"course_title": {"$in": course_titles}},  
        {"_id": 0, "course_code": 1, "course_title": 1, "course_type": 1, "semester": 1}
    ))

    # Store the first course & batch in session (or modify logic as needed)
    session["selected_course"] = batch_details[0]["course_title"]
    session["selected_batch"] = batch_details[0]["batch"]

    print(f"DEBUG: Stored in session -> Course: {session['selected_course']}, Batch: {session['selected_batch']}")

    # 🔹 Fetch COs (Course Outcomes) using `course_code`
    course_codes = [course["course_code"] for course in courses]
    cos = list(co_collection.find(
        {"course_code": {"$in": course_codes}},
        {"_id": 0, "co_no": 1, "co_des": 1, "co_level": 1, "is_approved": 1}
    ))

    # 🔹 Fetch faculty details (advisor name & department)
    faculty_info = faculty_collection.find_one({"pen_no": pen_no}, {"_id": 0, "name": 1, "dept_code": 1})
    advisor_name = faculty_info["name"] if faculty_info else "Unknown"
    department = faculty_info["dept_code"] if faculty_info else "Unknown"

    return render_template('f1.html',
                           faculty_name=session['name'],
                           semester=semester,
                           batch_details=batch_details,
                           cos=cos,
                           advisor_name=advisor_name,
                           department=department,
                           courses=courses)

@app.route("/get-advisor-batch", methods=["GET"])
def get_advisor_batch():
    if 'pen_no' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    pen_no = session['pen_no']
    faculty = faculty_collection.find_one({"pen_no": pen_no}, {"_id": 0, "role": 1})
    
    if not faculty or "advisor" not in faculty.get("role", {}):
        return jsonify({"error": "Not an advisor"}), 403

    advisor_batches = faculty["role"]["advisor"]
    latest_batch = max(advisor_batches, default=None)

    return jsonify({"batch": latest_batch})

    
@app.route('/advisor_dashboard')
def advisor_dashboard():
    if 'pen_no' not in session:
        return redirect(url_for('faculty_login_page'))

    pen_no = session['pen_no']

    # Fetch advisor batches
    faculty = faculty_collection.find_one({"pen_no": pen_no}, {"_id": 0, "name": 1, "role": 1})
    if not faculty or "advisor" not in faculty.get("role", {}):
        return redirect(url_for('faculty_dashboard'))  # Redirect if not an advisor

    advisor_batches = faculty["role"]["advisor"]

    # Fetch student details for these batches
    students = list(student_collection.find({"batch": {"$in": advisor_batches}}, {"_id": 0}))
    
    return render_template("advisor_dashboard.html", advisor=faculty, students=students)



@app.route("/course_mapping", methods=["POST", "GET"])
def course_mapping():
    if request.method == "POST":
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Empty JSON body"}), 400
        except Exception as e:
            return jsonify({"error": f"Invalid JSON format: {str(e)}"}), 400

        semester = data.get("semester")
        subject = data.get("subject")
        teacher = data.get("teacher")  # Teacher Name
        department = data.get("department")

        if not (semester and subject and teacher and department):
            return jsonify({"error": "Missing fields"}), 400

        # 🔹 Find pen_no using teacher name and department
        faculty = db.faculty.find_one({"name": teacher, "dept_code": department}, {"_id": 0, "pen_no": 1})
        if not faculty:
            return jsonify({"error": "Faculty not found"}), 404
        
        pen_no = faculty["pen_no"]

        # 🔹 Find the latest batch the faculty is an advisor of
        advisor_info = db.faculty.find_one({"pen_no": session["pen_no"]}, {"_id": 0, "role": 1})
        if not advisor_info or "advisor" not in advisor_info.get("role", {}):
            return jsonify({"error": "User is not an advisor"}), 403

        latest_batch = max(advisor_info["role"]["advisor"], default=None)

        if not latest_batch:
            return jsonify({"error": "No advisor batch found"}), 404

        # 🔹 Store into course_mapping
        new_mapping = db.course_mapping.insert_one({
            "name":teacher,
            "batch": latest_batch,
            "semester":semester,
            "course_title": subject,
            "pen_no": pen_no,
            "dept_code": department
        })

        return jsonify({
            "message": "Course mapping added successfully",
            "id": str(new_mapping.inserted_id)
        }), 200

    # If request is GET, check if a semester is selected
    selected_semester = request.args.get("semester")
    
    # Fetch subjects only for selected semester
    subjects = []
    if selected_semester:
        subjects = list(db.courses.find({"semester": selected_semester}, {"_id": 0, "course_title": 1}))

    # Fetch department dropdown
    departments = list(db.departments.find({}, {"_id": 0, "dept_code": 1, "dept_name": 1}))

    return render_template(
        "course-mapping.html",
        subjects=subjects,
        departments=departments
    )

# 🔹 Route to fetch subjects dynamically
@app.route("/get-subjects", methods=["GET"])
def get_subjects():
    semester = request.args.get("semester")
    if not semester:
        return jsonify({"error": "Semester is required"}), 400
    
    subjects = list(db.courses.find({"semester": semester}, {"_id": 0, "course_title": 1}))
    return jsonify({"subjects": subjects})


@app.route("/get-teachers", methods=["POST"])
def get_teachers():
    data = request.json
    selected_dept = data.get("department")

    if not selected_dept:
        return jsonify({"error": "Department not selected"}), 400

    # Fetch only teachers in the selected department
    teachers = list(db.faculty.find({"dept_code": selected_dept}, {"_id": 0, "name": 1}))

    return jsonify({"teachers": teachers})
    
# 🔹 UPDATE Course Mapping
@app.route("/edit-mapping/<mapping_id>", methods=["POST"])
def update_mapping(mapping_id):
    data = request.get_json()
    semester = data.get("semester")
    subject = data.get("subject")
    teacher = data.get("teacher")
    department = data.get("department")

    result = db.course_mapping.update_one(
        {"_id": ObjectId(mapping_id)},
        {"$set": {"batch": semester, "course_title": subject, "pen_no": teacher, "dept_code": department}}
    )

    if result.modified_count > 0:
        return jsonify({"message": "Course mapping updated successfully"}), 200
    return jsonify({"error": "No change made or mapping not found"}), 404

@app.route("/get-courses", methods=["GET"])
def get_courses():
    semester = request.args.get("semester")
    if not semester:
        return jsonify({"error": "Semester is required"}), 400

    courses = list(db.courses.find({"semester": semester}, {"_id": 0, "title": 1}))
    return jsonify({"courses": courses})

@app.route("/get-options")
def get_options():
    try:
        subjects = [course["course_title"] for course in db.courses.find({}, {"_id": 0, "course_title": 1})]
        teachers = [faculty["name"] for faculty in db.faculty.find({}, {"_id": 0, "name": 1})]
        departments = [dept["name"] for dept in db.departments.find({}, {"_id": 0, "dept_name": 1})]

        return jsonify({"subjects": subjects, "teachers": teachers, "departments": departments}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-latest-batch", methods=["GET"])
def get_latest_batch():
    pen_no=session.get("pen_no")
    if not pen_no:
        return jsonify({"error": "User not loggged in"}),401
    advisor = db.faculty.find_one({"pen_no": pen_no}, {"_id":0,"role.advisor": 1})
    if not advisor or "advisor" not in advisor.get("role", {}):
        return jsonify({"error": "User is not an advisor"}), 403
    
    latest_batch = max(advisor["role"]["advisor"], default=None)
    latest_semester = db.course_mapping.find_one({"batch": latest_batch}, sort=[("batch", -1)])
    print(latest_semester)

    if not latest_batch or not latest_semester:
        return jsonify({"error": "No batch/semester found"}), 404

    return jsonify({"batch": latest_batch, "semester": latest_semester["semester"]})

@app.route("/get-course-mappings", methods=["GET"])
def get_course_mappings():
    batch = request.args.get("batch")
    semester = request.args.get("semester")
    
    query = {}
    if batch:
        query["batch"] = batch
    if semester:
        query["semester"] = semester

    # Fetch course mappings
    mappings = list(db.course_mapping.find(query, {"_id": 1, "course_title": 1, "name": 1, "dept_code": 1}))
    print(mappings)
    # Convert ObjectId to string before returning JSON
    for mapping in mappings:
        mapping["_id"] = str(mapping["_id"])

    return jsonify({"mappings": mappings}),200

@app.route("/course_outcome")
def course_outcome():
    faculty_name = session.get("name")  # Fetch faculty name from session
    course_name = session.get("selected_course")  # Fetch selected course
    batch = session.get("selected_batch")  # Fetch selected batch
    department = session.get("dept_code")  # Fetch department (if stored in session)

    print(f"DEBUG: Course Outcome Page -> Faculty: {faculty_name}, Course: {course_name}, Batch: {batch}, Department: {department}")

    if not faculty_name or not course_name or not batch:
        flash("Invalid session data. Please reselect batch and course.", "error")
        return redirect(url_for("faculty_dashboard"))

    return render_template("faculty2.html",
                           faculty_name=faculty_name,
                           course_name=course_name,
                           batch=batch,
                           department=department)


# Route to add CO with faculty, course, and batch details
@app.route("/add_co", methods=["POST"])
def add_co():
    faculty_pen_no = session.get("pen_no")
    selected_course = session.get("selected_course")
    selected_batch = session.get("selected_batch")
    
    print("DEBUG: Session data ->", faculty_pen_no, selected_course, selected_batch)  # Debugging

    if not faculty_pen_no or not selected_course or not selected_batch:
        return jsonify({"message": "Unauthorized access or missing course selection!"}), 403

    # Get CO details from frontend
    co_no = request.form.get("co_no")
    description = request.form.get("description")
    bloom_level = request.form.get("bloom_level")
    threshold = request.form.get("threshold")

    if not all([co_no, description, bloom_level, threshold]):
        return jsonify({"message": "All fields are required!"}), 400

    # Validate if faculty is assigned to this course & batch
    assigned_course = mongo.db.course_mapping.find_one({
        "pen_no": faculty_pen_no,
        "course_title": selected_course,
        "batch": selected_batch
    })

    if not assigned_course:
        return jsonify({"message": "You are not assigned to this course and batch!"}), 403

    co_data = {
        "faculty_pen_no": faculty_pen_no,
        "course_name": selected_course,
        "batch": selected_batch,
        "co_no": co_no,
        "description": description,
        "bloom_level": int(bloom_level),
        "threshold": int(threshold),
        "is_approved": False
    }

    mongo.db.course_outcomes.insert_one(co_data)
    return jsonify({"message": "Course Outcome added successfully!"})

# Route to get COs for a faculty, course, and batch
@app.route("/get_cos", methods=["GET"])
def get_cos():
    faculty_pen_no = session.get("pen_no")
    selected_course = session.get("selected_course")
    selected_batch = session.get("selected_batch")
    


    if not faculty_pen_no or not selected_course or not selected_batch:
        return jsonify([])

    cos = list(mongo.db.course_outcomes.find({
        "faculty_pen_no": faculty_pen_no,
        "course_name": selected_course,
        "batch": selected_batch
    }))


    for co in cos:
        co["_id"] = str(co["_id"])  # Convert ObjectId to string

    return jsonify(cos)


# Route to edit CO
@app.route('/edit_co', methods=['POST'])
def edit_co():
    try:
        co_id = request.form.get('_id')  # Get `_id` from request
        description = request.form.get('description')
        bloom_level = request.form.get('bloom_level')
        threshold = request.form.get('threshold')

        if not co_id or not ObjectId.is_valid(co_id):  # Validate ObjectId
            return jsonify({"message": "Invalid CO ID"}), 400

        # Update CO in MongoDB
        result = db.course_outcomes.update_one(
            {"_id": ObjectId(co_id)},
            {"$set": {"description": description, "bloom_level": bloom_level, "threshold": threshold}}
        )

        if result.matched_count == 0:
            return jsonify({"message": "CO not found"}), 404

        return jsonify({"message": "CO updated successfully!"})
    

    except Exception as e:
        return jsonify({"message": str(e)}), 500
    
# Route to delete CO
@app.route("/delete_co", methods=["POST"])
def delete_co():
    co_id = request.form.get("_id")  # Use _id

    if not co_id:
        return jsonify({"message": "CO ID required!"}), 400

    mongo.db.course_outcomes.delete_one({"_id": ObjectId(co_id)})  # Query by _id
    return jsonify({"message": "CO deleted successfully!"})

# Route to fetch CO-PO correlation matrix
@app.route("/get_matrix", methods=["GET"])
def get_matrix():
    faculty_pen_no = session.get("pen_no")
    selected_course = session.get("selected_course")
    selected_batch = session.get("selected_batch")

    print(f"Debug: Faculty PEN_NO: {faculty_pen_no}, Course: {selected_course}, Batch: {selected_batch}")  # Debugging

    if not faculty_pen_no or not selected_course or not selected_batch:
        return jsonify([])

    # Fetch approved COs
    cos = list(mongo.db.course_outcomes.find({
        "faculty_pen_no": faculty_pen_no,
        "course_name": selected_course,
        "batch": selected_batch,
        "is_approved": True
    }))

    matrix_data = []
    for co in cos:
        co_number = co["co_no"]

        # Fetch stored PO correlations for this CO
        stored_values = list(mongo.db.co_po_matrix.find({  # ✅ Correct collection name
            "faculty_id": str(faculty_pen_no),  # Ensure string match
            "batch": str(selected_batch),
            "course_name": str(selected_course),
            "co_number": str(co_number)
        }))

        print("Debug: Retrieved PO correlations:", stored_values)  # Debugging

        # Default PO values (- if no correlation exists)
        po_correlations = {f"PO{i}": "-" for i in range(1, 13)}

        # Update with stored values
        for entry in stored_values:
            po_key = f"PO{entry['po_number']}"  
            po_correlations[po_key] = str(entry["value"])  

        matrix_data.append({
            "co_number": co_number,
            "po_correlations": po_correlations
        })

    print("Debug: Final Matrix Data:", matrix_data)  # Debugging
    return jsonify(matrix_data)

@app.route('/save_matrix', methods=['POST'])
def save_matrix():
    try:
        data = request.json
        matrix = data["matrix"]
        faculty_pen_no = session.get("pen_no")
        course_name = session.get("selected_course")
        batch = session.get("selected_batch")

        # Store in MongoDB
        for entry in matrix:
            matrix_collection.update_one(
                {"faculty_id": faculty_pen_no, "batch": batch, "course_name": course_name, 
                 "co_number": entry["co_number"], "po_number": entry["po_number"]},
                {"$set": {"value": entry["value"]}},
                upsert=True
            )

        return jsonify({"message": "Matrix saved successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/update_matrix', methods=['POST'])
def update_matrix():
    try:
        data = request.json
        faculty_pen_no = data.get("faculty_pen_no")
        batch = data.get("batch")
        course_name = data.get("course_name")
        co_number = data.get("co_number")
        po_number = int(data.get("po_number"))
        value = int(data.get("value"))

        if not all([faculty_pen_no, batch, course_name, co_number, po_number is not None]):
            return jsonify({"error": "Missing required data"}), 400

        # Update existing document
        mongo.db.co_po_matrix.update_one(
            {
                "faculty_id": faculty_pen_no,
                "batch": batch,
                "course_name": course_name,
                "co_number": co_number,
                "po_number": po_number
            },
            {"$set": {"value": value}},
            upsert=True  # Insert if not exists
        )

        return jsonify({"message": "Matrix updated successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/tool-selection')
def tool_selection():
    # Get faculty ID, batch, and course from session
    faculty_pen_no = session.get('faculty_id')  # Get faculty ID from session
    batch = session.get('selected_batch')  # Get selected batch
    course_name = session.get('selected_course')  # Get selected course
    
    # Fetch faculty details using faculty ID
    faculty = faculty_collection.find_one({"_id": ObjectId(faculty_pen_no)})
    
    if not faculty:
        return "Faculty not found", 404  # Handle case when faculty is not found
    
    # Fetch only approved COs for the faculty's batch and course
    approved_cos_cursor = db.co_po_matrix.find({
        "faculty_id": faculty["pen_no"],
        "batch": batch,
        "course_name": course_name
    })
    
    # Convert cursor to a list and print it
    approved_cos = list(approved_cos_cursor)
    print(approved_cos)  # Debugging

    # Get unique CO numbers (sorting and converting to set to ensure uniqueness)
    co_list = sorted(set(co["co_number"] for co in approved_cos))

    return render_template('faculty3.html', co_list=co_list)


@app.route('/get-approved-cos', methods=['GET'])
def get_approved_cos():
    faculty_pen_no = session.get('faculty_id')  # Get faculty ID from session
    batch = session.get('selected_batch')  # Get selected batch
    course_name = session.get('selected_course')  # Get selected course
    
    # Fetch approved COs for the specific faculty, batch, and course
    approved_cos = db.co_po_matrix.find({
        "faculty_id": faculty_pen_no,
        "batch": batch,
        "course_name": course_name
    })

    co_list = sorted(set(co["co_number"] for co in approved_cos))  # Get unique CO numbers
    
    return jsonify({'cos': co_list})

@app.route('/get-tools-for-course', methods=['GET'])
def get_tools_for_course():
    course_name = session.get('selected_course')  # Get selected course
    print(f"Selected course: '{course_name}'")  # Debugging output
    
    # Fetch all course titles to check for any mismatches
    courses = db.course_collection.find({}, {"course_title": 1})
    for course in courses:
        print(f"Available course: {course['course_title']}")  # Debugging output
    
    # Fetch the course schema from the course collection
    course = db.courses.find_one({"course_title": {"$regex": "^" + course_name + "$", "$options": "i"}})
       
    if course is None:
        print(f"Course '{course_name}' not found.")
        return jsonify({'error': 'Course not found'}), 404
    
    course_schema = course.get("schema_name", "Schema not found")

    # Fetch the tools that match the course schema
    tools_cursor = db.tools.find({"schema_name": {"$regex": f"^{course_schema}$", "$options": "i"}})
    tools_list_raw = list(tools_cursor)  # ✅ Store the list first


    tools_list = [{"tool_name": tool["tool_name"]} for tool in tools_list_raw]  # ✅ Process from stored list


    return jsonify({'tools': tools_list})

@app.route('/save-tool-data', methods=['POST'])
def save_tool_config():
    data = request.json
    faculty_id = session.get('faculty_id')
    course = session.get('selected_course')
    batch = session.get('selected_batch')

    if not faculty_id or not course or not batch:
        return jsonify({"success": False, "message": "Session expired. Please log in again."}), 401

    tool_data = data.get('toolData', [])

    if not tool_data:
        return jsonify({"success": False, "message": "No tools selected!"}), 400

    # Store in MongoDB
    tool_config_collection.delete_many({"faculty_id": faculty_id, "course": course, "batch": batch})  # Remove previous data

    tool_config_collection.insert_many([
        {
            "faculty_id": faculty_id,
            "course": course,
            "batch": batch,
            "tool_name": tool["tool_name"],
            "tool_number": tool["tool_number"],
            "thresholds": tool["thresholds"],
        }
        for tool in tool_data
    ])

    return jsonify({"success": True, "message": "Tool configuration saved successfully!"})

@app.route('/get-saved-tool-data', methods=['GET'])
def get_saved_tool_data():
    faculty_id = session.get('faculty_id')
    course = session.get('selected_course')
    batch = session.get('selected_batch')
    print(f"Fetching saved tools for Faculty ID: {faculty_id}, Course: {course}, Batch: {batch}")
    data = list(db.tool_config.find(
        {"faculty_id": faculty_id, "course": course, "batch": batch}, 
        {"_id": 0, "tool_name": 1, "tool_number": 1, "thresholds": 1}
    ))    
    print(data)
    return jsonify(data)

@app.route('/delete-tool-data', methods=['POST'])
def delete_tool_data():
    tool_name = request.json.get("tool_name")
    faculty_id = session.get('faculty_id')
    course = session.get('selected_course')
    batch = session.get('selected_batch')


    db.tool_config.update_one(
        {"faculty_id": faculty_id, "course": course, "batch": batch},
        {"$pull": {"tools": {"tool_name": tool_name}}}
    )
    return jsonify({"message": "Tool deleted successfully!"})





@app.route('/mark-upload', methods=['GET'])
def mark_upload():
    if 'selected_course' not in session or 'selected_batch' not in session:
        return redirect(url_for('faculty_dashboard'))  # Ensure session has course/batch

    selected_course = session['selected_course']
    selected_batch = session['selected_batch']
    faculty_id = session.get('faculty_id')

    # Fetch students for the selected batch
    students = list(db.students.find({"batch": selected_batch}, {"_id": 0, "name": 1}))

    # Fetch tool configuration
    tool_config = list(db.tool_config.find({
    "course": selected_course,
    "batch": selected_batch,
    "faculty_id": faculty_id
}, {"_id": 0}))
    
    
    # Ensure tool_config exists
    if not tool_config:
        tool_config = {"tools": []}  # Default empty list for tools

    return render_template('faculty5.html', students=students, tool_config=tool_config)


@app.route("/get-questions", methods=["GET"])
def get_questions():
    batch = request.args.get("batch")
    course_name = request.args.get("course_name")

    if not batch or not course_name:
        return jsonify({"error": "Batch and Course Name are required"}), 400

    # Query MongoDB to fetch questions and their corresponding COs
    questions = list(db.questions.find({"batch": batch, "course_name": course_name}, {"_id": 0, "question": 1, "co": 1}))

    return jsonify({"questions": questions}), 200

@app.route('/get-mapped-courses', methods=['GET'])
def get_mapped_courses():
    faculty_id = session.get('faculty_id')
    if not faculty_id:
        return jsonify({"error": "Faculty not logged in"}), 401

    mapped_courses = list(db.course_mapping.find(
        {"faculty_pen_no": faculty_id},
        {"_id": 0, "batch": 1, "course_title": 1}
    ))

    return jsonify({"mapped_courses": mapped_courses}), 200

@app.route('/get-students', methods=['GET'])
def get_students():
    batch = request.args.get('batch')
    if not batch:
        return jsonify({"error": "Batch not provided"}), 400

    students = list(db.students.find({"batch": batch}, {"_id": 0, "name": 1}))
    return jsonify({"students": students}), 200

@app.route('/confirm-format', methods=['POST'])
def confirm_format():
    data = request.json
    batch = data.get('batch')
    course_name = data.get('course_name')
    students = data.get('students')

    if not batch or not course_name or not students:
        return jsonify({"error": "Missing data"}), 400

    db.csv_format.insert_one({
        "batch": batch,
        "course_name": course_name,
        "students": students
    })

    return jsonify({"message": "Format confirmed successfully!"}), 200



ALLOWED_EXTENSIONS = {'csv'}
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload-marks', methods=['POST'])
def upload_marks():
    try:
        if 'file' not in request.files:
            print("No file part in request")  # Debug log
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            print("No selected file")  # Debug log
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            print(f"Processing file: {file.filename}")  # Debug log

            # Read CSV
            df = pd.read_csv(file)

            # Pass df to process_marks
            return process_marks(df)

        return jsonify({'error': 'Invalid file format. Please upload a CSV file.'}), 400

    except Exception as e:
        print(f"🔥 Error: {str(e)}")  # Print error in Flask console
        return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500

@app.route('/confirm-tool-config', methods=['POST'])
def confirm_tool_config():
    faculty_session_id = session.get('faculty_id')  # Get faculty session ID
    if not faculty_session_id:
        return jsonify({"error": "Faculty not logged in"}), 401

    # Get faculty pen_no
    faculty = db.faculty.find_one({"_id": ObjectId(faculty_session_id)}, {"_id": 0, "pen_no": 1})
    if not faculty:
        return jsonify({"error": "Faculty record not found"}), 404

    faculty_pen_no = faculty["pen_no"]

    # Get batch and course from course_mapping
    faculty_course = db.course_mapping.find_one({"pen_no": faculty_pen_no}, {"_id": 0, "batch": 1, "course_title": 1})
    if not faculty_course:
        return jsonify({"error": "No mapped course found for faculty"}), 404

    selected_batch = faculty_course["batch"]
    selected_course = faculty_course["course_title"]

    # Get tool details from request
    tool_data = request.json
    tool_name = tool_data.get("tool_name")
    
    if not tool_name:
        return jsonify({"error": "Tool name missing"}), 400

    # Delete existing tool config if present
    db.questions.delete_many({"tool_name": tool_name, "batch": selected_batch, "course_name": selected_course})

    # Insert new tool config
    tool_data["batch"] = selected_batch
    tool_data["course_name"] = selected_course
    db.questions.insert_one(tool_data)

    return jsonify({"message": "Tool details confirmed and saved successfully!"}), 200


@app.route('/generate-csv', methods=['GET'])
def generate_csv():
    try:
        print("📂 Generating CSV...")

        faculty_session_id = session.get('faculty_id')
        if not faculty_session_id:
            return jsonify({"error": "Faculty not logged in"}), 401

        # Fetch faculty's pen_no
        faculty = db.faculty.find_one({"_id": ObjectId(faculty_session_id)}, {"_id": 0, "pen_no": 1})
        if not faculty:
            return jsonify({"error": "Faculty record not found"}), 404

        faculty_pen_no = faculty["pen_no"]

        # Fetch batch and course from course_mapping
        faculty_course = db.course_mapping.find_one({"pen_no": faculty_pen_no}, {"_id": 0, "batch": 1, "course_title": 1})
        if not faculty_course:
            return jsonify({"error": "No mapped course found for faculty"}), 404

        selected_batch = faculty_course["batch"]
        selected_course = faculty_course["course_title"]

        print(f"🔍 Selected Batch: {selected_batch}, Course: {selected_course}")

        # Fetch students
        students = list(db.students.find({"batch": selected_batch}, {"_id": 0, "univ_no": 1, "name": 1}))
        if not students:
            print("⚠️ No students found!")
            return jsonify({"error": "No students found"}), 400

        print(f"✅ Found {len(students)} students")

        # Fetch questions
        # Ensure the tool name is retrieved from the session or request
        selected_tool = session.get('selected_tool')  # Or retrieve from request

        tool_name = request.args.get("tool_name")
        if not tool_name:
            return jsonify({"error": "Tool name missing"}), 400

        # Fetch only questions for the selected tool, batch, and course
        question_data = list(db.questions.find(
            {"batch": selected_batch, "course_name": selected_course, "tool_name": tool_name},
            {"_id": 0,"parts": 1}
        ))
        print(question_data)

        if not question_data:
            print("⚠️ No questions found!")
            return jsonify({"error": "No questions found"}), 400

        print(f"✅ Found {len(question_data)} tool configurations")

        # Extract all questions
        questions = []
        for q in question_data:
            for part in q.get("parts", []):
                print(f"🛠 Processing Part: {part.get('part_label', 'Unknown')}")
                if isinstance(part, dict) and "questions" in part:
                    for question in part["questions"]:
                        print(f"📌 Found Question: {question}")
                        if isinstance(question, dict):
                            questions.append({
                                "question_no": question.get("question_no", ""),
                                "co": question.get("co", ""),
                                "total_marks": question.get("total_marks", "")
                            })

        if not questions:
            print("⚠️ No valid questions extracted!")
            return jsonify({"error": "No valid questions found"}), 400

        print(f"✅ Extracted {len(questions)} questions")

        # Generate CSV file path
        file_path = f"static/{selected_course}_{selected_batch}_marks.csv"
        print(f"📄 Writing CSV to: {file_path}")

        with open(file_path, "w", newline="") as file:
            writer = csv.writer(file)

            # Header row
            headers = ["KTU ID", "Student Name"] + [f"Q{q['question_no']}" for q in questions]
            writer.writerow(headers)
            print("✅ Header written:", headers)

            # Max Marks row
            max_marks_row = ["", ""] + [q["total_marks"] for q in questions]
            writer.writerow(max_marks_row)
            print("✅ Max Marks written:", max_marks_row)

            # CO row
            co_row = ["", ""] + [f"CO{q['co']}" for q in questions]
            writer.writerow(co_row)
            print("✅ CO row written:", co_row)

            # Student rows (empty marks for now)
            for student in students:
                row_data = [student.get("univ_no", ""), student.get("name", "")] + [""] * len(questions)
                writer.writerow(row_data)
                print("✅ Student row written:", row_data)
        if os.path.exists(file_path):
            print(f"✅ CSV file exists at: {file_path}")
        else:
            print(f"❌ CSV file NOT found at: {file_path}")

        print("🎉 CSV Generation Completed!")
        return jsonify({"message": "CSV generated successfully.", "file_url": f"/{file_path}"}), 200

    except Exception as e:
        print(f"🔥 Error generating CSV: {e}")
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500
    
def process_marks(df):
    try:
        # ✅ 1. Remove empty rows to prevent index misalignment
        df = df.dropna(how="all").reset_index(drop=True)

        # ✅ 2. Extract headers, total marks, and CO mapping row
        column_headers = df.iloc[0].tolist()
        co_mapping_row = df.iloc[2].tolist()

        # ✅ 3. Assign correct column names
        student_marks = df.iloc[3:].reset_index(drop=True)
        expected_columns = ["KTU ID", "Student Name"] + [f"Q{i}" for i in range(1, len(column_headers) - 1)]
        student_marks.columns = expected_columns

        # ✅ 4. Ensure "Student Name" column exists before proceeding
        if "Student Name" not in student_marks.columns:
            raise ValueError("Column 'Student Name' is missing or misaligned.")

        # ✅ 5. Remove "KTU ID" if present (optional)
        if "KTU ID" in student_marks.columns:
            student_marks.drop(columns=["KTU ID"], inplace=True)

        # ✅ 6. Build CO mapping dictionary
        course_name = session.get('selected_course', "Unknown Course")
        batch = session.get('selected_batch', "Unknown Batch")

        # ✅ Fetch question data to get **correct COs**  
        question_data = db.questions.find_one(
            {"batch": batch, "course_name": course_name}, 
            {"_id": 0, "parts.questions": 1}
        )
        if not question_data:
            return jsonify({"error": "No question data found"}), 400

        # ✅ Extract COs dynamically from question bank
        co_questions = {}
        for part in question_data.get("parts", []):
            for q in part["questions"]:
                co_label = f"CO{q['co']}"
                co_questions.setdefault(co_label, []).append(q)

        # ✅ Fetch CO Thresholds
        course_outcomes = db.course_outcomes.find(
            {"course_name": course_name, "batch": batch}, 
            {"_id": 0, "co_no": 1, "threshold": 1}
        )
        thresholds = {f"CO{co_doc['co_no']}": co_doc["threshold"] for co_doc in course_outcomes}

        # ✅ Compute Student CO Attainment
        student_co_attainment = []
        for _, row in student_marks.iterrows():
            student_name = row["Student Name"]
            co_scores = {}

            for co_label, questions in co_questions.items():
                obtained_marks = 0
                compulsory_marks_total = 0
                optional_marks_attended = 0

                for question in questions:
                    question_col = f"Q{question['question_no']}"
                    if question_col in row and pd.notna(row[question_col]):
                        obtained_marks += float(row[question_col])
                        if question["compulsory"]:
                            compulsory_marks_total += float(question["total_marks"])
                        else:
                            optional_marks_attended += float(question["total_marks"])

                total_marks_possible = compulsory_marks_total + optional_marks_attended
                co_attainment = (obtained_marks / total_marks_possible) * 100 if total_marks_possible > 0 else 0
                co_scores[co_label] = co_attainment

            student_co_attainment.append({"student_name": student_name, **co_scores})

        # ✅ Convert to DataFrame
        attainment_df = pd.DataFrame(student_co_attainment)

        # ✅ Compute Class CO Attainment %
        co_threshold_results = {}
        total_students = len(attainment_df)

        for co_label, threshold in thresholds.items():
            if co_label in attainment_df:
                passing_students = sum(attainment_df[co_label] >= threshold)
                percentage_passing = (passing_students / total_students) * 100 if total_students > 0 else 0
                co_threshold_results[co_label] = percentage_passing

        # ✅ Save to MongoDB
        db.attainment_results.insert_one({
            "batch": batch,
            "course_name": course_name,
            "tool_name": "ASSIGNMENT 1",
            "co_attainment": co_threshold_results
        })

        return jsonify({"message": "Marks processed successfully", "co_attainment_percentage": co_threshold_results}), 200

    except Exception as e:
        print(f"🔥 Error: {str(e)}")
        return jsonify({"error": f"Processing Error: {str(e)}"}), 500

@app.route('/enter-co-questions', methods=['GET', 'POST'])
def enter_co_questions():
    faculty_session_id = session.get('faculty_id')
    if not faculty_session_id:
        return jsonify({"error": "Faculty not logged in"}), 401

    faculty = db.faculty.find_one({"_id": ObjectId(faculty_session_id)}, {"_id": 0, "pen_no": 1})
    if not faculty:
        return jsonify({"error": "Faculty record not found"}), 404

    faculty_pen_no = faculty["pen_no"]
    course_mapping = db.course_mapping.find_one({"pen_no": faculty_pen_no}, {"_id": 0, "batch": 1, "course_title": 1})
    
    if not course_mapping:
        return jsonify({"error": "No mapped course found"}), 404

    batch = course_mapping["batch"]
    course_name = course_mapping["course_title"]

    # Fetch available COs for the subject
    co_list = list(db.course_outcomes.find({"course_name": course_name, "batch": batch}, {"_id": 0, "co_no": 1}))

    if request.method == 'POST':
        data = request.json
        db.co_questions.update_one(
    {
        "faculty_pen_no": faculty_pen_no,
        "batch": batch,
        "course_name": course_name
    },
    {
        "$set": { "questions": data["questions"] }
    },
    upsert=True
    )

        return jsonify({"message": "Questions saved successfully!"})

    return render_template('survey.html', co_list=co_list, batch=batch, course_name=course_name)

@app.route('/submit_scales', methods=['POST'])
def submit_scales():
    try:
        data = request.json
        print("Received Data:", data)  # Debugging

        course_name = data.get("course_name")
        batch = data.get("batch")
        questions = data.get("questions", {})
        scales = data.get("scales", {})

        if not course_name or not batch:
            print("Error: Missing course_name or batch")  # Debugging
            return jsonify({"error": "Missing course_name or batch"}), 400

        for co, values in scales.items():
            print(f"Processing CO: {co}, Scales: {values}")  # Debugging

            sorted_counts = sorted(values.items(), key=lambda x: int(x[0]), reverse=True)
            top_3_scales = sorted_counts[:2]
            top_3_students = sum(count for _, count in top_3_scales)
            total_students = sum(count for _, count in sorted_counts)

            top_3_avg = (top_3_students / total_students) * 100 if total_students > 0 else 0

            result = db.scale_results.update_one(
                {"batch": batch, "course_name": course_name, "co": co},
                {
                    "$set": {
                        "question": questions.get(co, ""),
                        "scales": values,
                        "top_3_avg": top_3_avg,
                        "total_students": total_students
                    }
                },
                upsert=True
            )
            print(f"Stored Data for CO {co}, Matched: {result.matched_count}, Modified: {result.modified_count}")  # Debugging

        return jsonify({"message": "Scale data stored successfully!"})

    except Exception as e:
        print("Error:", str(e))  # Debugging
        return jsonify({"error": str(e)}), 500
    
@app.route('/external-marks-entry', methods=['GET'])
def external_marks_entry():
    faculty_pen_no = session.get("pen_no")
    course_name = session.get("selected_course")
    batch = session.get("selected_batch")

    co_list = list(db.course_outcomes.find(
        {"course_name": course_name, "batch": batch, "faculty_pen_no": faculty_pen_no},
        {"_id": 0, "co_no": 1}
    ))

    co_nos = [co["co_no"] for co in co_list]  # Convert to a simple list

    threshold_doc = db.thresholds.find_one({"pen_no": faculty_pen_no, "course": course_name})
    if not threshold_doc:
        return "Threshold not set for this faculty and course.", 400

    return render_template("faculty8.html", 
                           faculty_pen_no=faculty_pen_no, 
                           course_name=course_name, 
                           batch=batch, 
                           co_no=co_nos, 
                           threshold=threshold_doc.get("external_th"),
                           grades=threshold_doc.get("external_grade"))

@app.route('/submit-external-marks', methods=['POST'])
def submit_external_marks():
    data = request.json
    faculty_pen_no = data.get("faculty_pen_no")
    course_name = data.get("course_name")
    batch = data.get("batch")
    achievement_percentage = data.get("achievement_percentage")
    co_nos = data.get("co_nos")  # Now a list of CO numbers

    if not co_nos:
        return jsonify({"error": "No COs found for this course"}), 400

    for co_no in co_nos:
        db.achievements_collection.update_one(
            {"faculty_pen_no": faculty_pen_no, "course_name": course_name, "batch": batch, "co_no": co_no},
            {"$set": {"achievement_percentage": achievement_percentage}},
            upsert=True
        )

    return jsonify({"message": "CO achievement percentages updated successfully!"}), 200

@app.route('/course-attain', methods=['GET'])
def course_attain():
    course = session.get("selected_course")  # Fetch selected course
    batch = session.get("selected_batch")  # Fetch selected batch
    department = session.get("dept_code") 

    # Fetch tool weightage and attainment results
    tool_configs = list(db.tool_config.find({"batch": batch, "course": course}))
    attainment_results = list(db.attainment_results.find({"batch": batch, "course_name": course}))
    university_results = list(db.achievements_collection.find({"batch": batch, "course_name": course}))
    thresholds = db.thresholds.find_one({"course": course})
    survey_results = list(db.scale_results.find({"batch": batch, "course_name": course}))
    benchmark = db.Benchmark.find_one({"dept_code": department})
    
    # Step 1: Compute total weightage for each CO
    co_total_weightage = {}
    internal_attainment = {}

    for tool in tool_configs:
        tool_name = f"{tool['tool_name'].strip().upper()} {tool['tool_number']}"  # Normalize name
        weightage = tool['thresholds'][0]  # First threshold is for internal

        attainment = next((res['co_attainment'] for res in attainment_results if res['tool_name'].strip().upper() == tool_name), {})

        for co in attainment.keys():
            co_total_weightage[co] = co_total_weightage.get(co, 0) + weightage

    # Step 2: Compute weighted internal attainment for each CO
    for tool in tool_configs:
        tool_name = f"{tool['tool_name'].strip().upper()} {tool['tool_number']}"  # Normalize name
        weightage = tool['thresholds'][0]  

        attainment = next((res['co_attainment'] for res in attainment_results if res['tool_name'].strip().upper() == tool_name), {})

        for co, percentage in attainment.items():
            if co_total_weightage[co] > 0:
                internal_attainment[co] = internal_attainment.get(co, 0) + (percentage * weightage / co_total_weightage[co])

    print("Internal Attainment:", internal_attainment)

    # Step 3: Calculate external attainment from university-level assessment
    external_attainment = {str(res['co_no']): res['achievement_percentage'] for res in university_results}  # Ensure string keys
    print("External Attainment:", external_attainment)

    # Step 4: Compute overall direct attainment
    direct_attainment = {}
    internal_th = thresholds['internal_th']
    external_th = thresholds['external_th']

    for co in internal_attainment.keys():
        direct_attainment[co] = ((internal_attainment.get(co, 0) * internal_th / 100) +
                                 (external_attainment.get(co, 0) * external_th / 100))

    print("Direct Attainment:", direct_attainment)

    # Step 5: Compute Indirect Attainment (Survey Data)
    indirect_attainment = {f"CO{res['co']}": res['top_3_avg'] for res in survey_results}  # Ensure "CO" prefix
    print("Indirect Attainment:", indirect_attainment)

    # Step 6: Determine Levels for Direct & Indirect Attainment Based on Benchmark
    direct_levels = {}
    indirect_levels = {}

    level_3_threshold = benchmark["co_attainment"]["level3"]
    level_2_threshold = benchmark["co_attainment"]["level2"]
    level_1_threshold = benchmark["co_attainment"]["level1"]

    for co, value in direct_attainment.items():
        if value >= level_3_threshold:
            direct_levels[co] = 3
        elif value >= level_2_threshold:
            direct_levels[co] = 2
        else:
            direct_levels[co] = 1

    for co, value in indirect_attainment.items():
        if value >= level_3_threshold:
            indirect_levels[co] = 3
        elif value >= level_2_threshold:
            indirect_levels[co] = 2
        else:
            indirect_levels[co] = 1

    print("Direct Levels:", direct_levels)
    print("Indirect Levels:", indirect_levels)

    # Step 7: Compute Final Overall Attainment Using Threshold-Weighted Levels
    final_co_attainment = {}
    direct_threshold = benchmark['direct_threshold'] / 100  # Convert % to fraction
    indirect_threshold = benchmark['indirect_threshold'] / 100  # Convert % to fraction

    for co in direct_levels.keys():
        direct_level = direct_levels.get(co, 1)  # Default to 1 if missing
        indirect_level = indirect_levels.get(co, 1)  # Default to 1 if missing

        final_co_attainment[co] = float(direct_level * direct_threshold) + float(indirect_level * indirect_threshold)

    print("Final CO Attainment:", final_co_attainment)
    
    db.final.update_one(
    {"batch": batch, "course_name": course},  # Find the document
    {"$set": {"final_co_attainment": final_co_attainment}},  # Update the field
    upsert=True  # Create a new document if it doesn’t exist
)


    return render_template("faculty6.html",
                        final_co_attainment=final_co_attainment,
                        direct_levels=direct_levels,
                        indirect_levels=indirect_levels)

if __name__ == '__main__':
    app.run(debug=True)
