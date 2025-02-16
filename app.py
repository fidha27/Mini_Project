from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB URI
db = client["miniproject"]  # Database name

@app.route("/")
def index():
    # Fetch all students from the MongoDB collection
    students = list(db.students.find({}, {"_id": 0}))  # Exclude MongoDB's default `_id` field

    # Fetch the advisor's name
    advisor = db.advisor.find_one({}, {"_id": 0})  # Fetch the first advisor

    return render_template("advisor1.html", students=students, advisor=advisor)

if __name__ == "__main__":
    app.run(debug=True)