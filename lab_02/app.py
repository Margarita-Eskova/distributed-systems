from flask import Flask, jsonify, request
import datetime

app = Flask(__name__)

# База данных в памяти
jobs = [
    {
        "id": 1,
        "job_title": "Python Developer",
        "company": "TechCorp",
        "timestamp": datetime.datetime.now().isoformat()
    },
    {
        "id": 2,
        "job_title": "Junior Frontend Developer",
        "company": "WebStudio",
        "timestamp": datetime.datetime.now().isoformat()
    }
]
next_id = 3

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    return jsonify({"jobs": jobs})

@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    job = next((j for j in jobs if j["id"] == job_id), None)
    if job is None:
        return jsonify({"error": "Вакансия не найдена"}), 404
    return jsonify(job)

@app.route('/api/jobs', methods=['POST'])
def create_job():
    global next_id
    if not request.json or not request.json.get('job_title') or not request.json.get('company'):
        return jsonify({"error": "Необходимо передать JSON с полями job_title и company"}), 400
    
    new_job = {
        "id": next_id,
        "job_title": request.json['job_title'],
        "company": request.json['company'],
        "timestamp": datetime.datetime.now().isoformat()
    }
    jobs.append(new_job)
    next_id += 1
    return jsonify(new_job), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
