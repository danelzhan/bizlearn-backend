import os, json
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from pymongo import MongoClient, ASCENDING
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)


client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DB_NAME")]
courses = db.courses

def serialize(doc):
    if not doc: return None
    doc["_id"] = str(doc["_id"])
    return doc

@app.get("/api/courses/<slug>")
def get_course_by_id(slug):
    db = client['BizLearn']
    collection = db['courses']
    
    doc = collection.find_one({"slug": slug})
    if not doc:
        return {"error": "Not found"}, 404
    doc["_id"] = str(doc["_id"])
    return doc 

@app.get("/api/courses/<slug>/lessons/<id>")
def get_lesson_by_id(slug, id):
    db = client["BizLearn"]
    collection = db["courses"]

    course = collection.find_one({"slug": slug}, {"_id": 0, "title": 1, "lessons": 1})
    if not course:
        abort(404, "course not found")

    lesson = None

    for l in course["lessons"]:
        if str(l.get("id")) == id or l.get("slug") == id:
            lesson = l
            break

    if lesson is None:
        abort(404, "lesson not found")
    
    return jsonify(lesson)

# def delete_course_by_id(course_id):
#     db = client['BizLearn']
#     collection = db['courses']

#     query = {"_id": course_id}
    
#     result = collection.delete_one(query)
#     return result.deleted_count

@app.get("/api/users/<email>")
def get_user_by_email(email):
    db = client['BizLearn']
    collection = db['users']

    doc = collection.find_one({"email": email})
    if not doc:
        return jsonify({"error": "Not found"})
    doc["_id"] = str(doc["_id"])
    return jsonify(doc)

@app.post("/api/users")
def add_user():
    db = client['BizLearn']
    collection = db['users']

    user_data = request.get_json()
    
    if 'email' not in user_data:
        raise ValueError("user data not in correct form.")
    
    collection.insert_one(user_data)
    
    return jsonify(user_data)

@app.patch("/api/users/<email>")
def update_user(email):
    db = client['BizLearn']
    collection = db['users']

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    result = collection.update_one({"email": email}, {"$set": data})

    if result.matched_count == 0:
        return jsonify({"error": "User not found"}), 404
    
    return "success", 200

@app.patch("/api/users/<email>/courses/<slug>/code")
def update_user_code(email, slug):
    db = client['BizLearn']
    collection = db['users']

    data = request.get_json()
    new_html = data.get("html", "")
    new_css = data.get("css", "")
    new_js = data.get("js", "")

    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    collection.update_one(
        {"email": email, "courses_enrolled.slug": slug},
        {
            "$set": {
                "courses_enrolled.$.saved_html": new_html,
                "courses_enrolled.$.saved_css": new_css,
                "courses_enrolled.$.saved_js": new_js
            }
        }
    )
    
    return "success", 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)