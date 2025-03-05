from flask import render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Topic, Question, Score
from utils import evaluate_code
from datetime import datetime


def get_user_by_username(uname):
    user = User.query.filter_by(uname=uname).first() 
    return user

def get_user_from_database(id):
    user = User.query.get(id) 
    if user:
        print(f"User found: {user.uname}")
        return {
            'id': user.id,
            'fname': user.fname,
            'sname': user.sname,
            'uname': user.uname,
            'email': user.email
        }
    return None



def register_routes(app, db, bcrypt):

    @app.route('/')
    def home():
        return app.send_static_file('index.html')

    @app.route('/login', methods=['POST'])
    def login():
        if not request.is_json:
            return jsonify({"message": "Request must be JSON"}), 400

        data = request.get_json()
        uname = data.get('uname')
        pword = data.get('pword')

        if not uname or not pword:
            return jsonify({"message": "Username and password are required"}), 400

        user = get_user_by_username(uname)

        if user and bcrypt.check_password_hash(user.pword, pword):
            session["user_id"] = user.id  
            return jsonify({
                "id": user.id,
                "message": "Login successful"
            }), 200

        return jsonify({"message": "Invalid credentials"}), 401


    @app.route('/register', methods=['POST'])
    def register():
        if not request.is_json:
            return jsonify({"message": "Request must be JSON"}), 400

        data = request.get_json()
        fname = data.get('fname')
        sname = data.get('sname')
        email = data.get('email')
        uname = data.get('uname')
        pword = data.get('pword')

        if not all([fname, sname, email, uname, pword]):
            return jsonify({"message": "All fields are required"}), 400

        hashed_password = bcrypt.generate_password_hash(pword).decode('utf-8')
        new_user = User(fname=fname, sname=sname, email=email, uname=uname, pword=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"message": "User registered successfully"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error occurred while registering user", "error": str(e)}), 500

    @app.route("/logout", methods=["POST", "GET"])
    def logout():
        session.pop("user", None)
        return redirect(url_for("login"))


    @app.route('/profile/<int:id>', methods=['GET'])
    def get_profile(id):
        user = get_user_from_database(id) 
        if user:
            user_data = {
                'id': user.id,
                'fname': user.fname,
                'sname': user.sname,
                'email': user.email,
                'uname': user.uname
            }
            return jsonify(user_data) 
        else:
            return jsonify({"error": "User not found"}), 404
        
    @app.route('/get_user_id', methods=['GET'])
    def get_user_id():
        id = session.get("id")
        if id:
            return jsonify({"id": id})
        return jsonify({"error": "User not logged in"}), 401


    @app.route('/api/topics', methods=["GET"])
    def api_topics():
        topics = Topic.query.all()
        topics_data = [{"id": topic.id, "name": topic.name} for topic in topics]
        return jsonify(topics_data)


    @app.route('/api/topic_details/<int:topic_id>', methods=["GET"])
    def api_topic_details(topic_id):
        topic = Topic.query.get_or_404(topic_id)
        topic_data = {
            "id": topic.id,
            "name": topic.name,
            "description": topic.description,
            "questions": [{"id": q.id, "text": q.question_text} for q in topic.questions]
        }
        return jsonify(topic_data)


    @app.route('/api/quiz/<int:topic_id>', methods=["POST"])
    def api_quiz(topic_id):
        topic = Topic.query.get_or_404(topic_id)
        questions = Question.query.filter_by(topic_id=topic_id).all()
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "You need to log in to take a quiz."}), 403
        
        score = 0
        feedback = []

        for question in questions:
            user_answer = request.json.get(str(question.id))

            if question.question_type == 'multiple-choice':
                if user_answer == question.correct_answer:
                    score += 1
            elif question.question_type == 'code-snippet':
                test_cases = question.test_cases
                is_correct, results = evaluate_code(user_answer, test_cases)

                if is_correct:
                    score += 1
                else:
                    failed_cases = [
                        f"Input: {tc['input']} | Expected: {tc['output']} | Got: {res}"
                        for tc, res in zip(test_cases, results) if not res
                    ]
                    feedback.append(f"Question: {question.question_text}\nFailed Cases:\n" + "\n".join(failed_cases))

        existing_score = Score.query.filter_by(user_id=user_id, topic_id=topic_id).first()
        if existing_score:
            existing_score.attempts += 1
            existing_score.last_score = score
            existing_score.last_attempt_date = datetime.utcnow()
            existing_score.highest_score = max(existing_score.highest_score, score)
            existing_score.lowest_score = min(existing_score.lowest_score, score)
            db.session.commit()
        else:
            new_score = Score(
                user_id=user_id,
                topic_id=topic_id,
                attempts=1,
                highest_score=score,
                lowest_score=score,
                last_score=score
            )
            db.session.add(new_score)
        
        db.session.commit()

        return jsonify({
            "score": score,
            "total_questions": len(questions),
            "feedback": feedback
        })

