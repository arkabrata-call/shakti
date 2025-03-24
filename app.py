# Basic project structure for Flask backend

# app.py - Main application file
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///shaktirise.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS for frontend integration
CORS(app)

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    location = db.Column(db.String(100))
    district = db.Column(db.String(100))
    state = db.Column(db.String(100))
    business_description = db.Column(db.Text)
    preferred_language = db.Column(db.String(50))
    password_hash = db.Column(db.String(200))
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='user', lazy=True)
    progress_records = db.relationship('Progress', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # business, financial, digital, leadership
    language = db.Column(db.String(50))
    duration_weeks = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    modules = db.relationship('Module', backref='course', lazy=True)
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, nullable=False)
    
    # Relationships
    lessons = db.relationship('Lesson', backref='module', lazy=True)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    order = db.Column(db.Integer, nullable=False)
    
    # Relationships
    resources = db.relationship('Resource', backref='lesson', lazy=True)
    quizzes = db.relationship('Quiz', backref='lesson', lazy=True)

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50))  # video, pdf, audio, etc.
    url = db.Column(db.String(255))
    is_downloadable = db.Column(db.Boolean, default=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50))  # multiple-choice, true-false, text
    
    # Relationships
    options = db.relationship('Option', backref='question', lazy=True)

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    option_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    completion_date = db.Column(db.DateTime)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    status = db.Column(db.String(50))  # not-started, in-progress, completed
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    completion_date = db.Column(db.DateTime)

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Float)
    attempt_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_passed = db.Column(db.Boolean, default=False)

class Discussion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    replies = db.relationship('Reply', backref='discussion', lazy=True)

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if user already exists
    existing_user = User.query.filter_by(phone=data.get('phone')).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'Phone number already registered'}), 400
    
    # Create new user
    new_user = User(
        name=data.get('name'),
        phone=data.get('phone'),
        location=data.get('location'),
        district=data.get('district'),
        state=data.get('state'),
        business_description=data.get('business'),
        preferred_language=data.get('language')
    )
    new_user.set_password(data.get('password', '123456'))  # Default password or set by user
    
    try:
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return jsonify({'success': True, 'message': 'Registration successful', 'user_id': new_user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(phone=data.get('phone')).first()
    
    if user and user.check_password(data.get('password')):
        login_user(user)
        return jsonify({'success': True, 'message': 'Login successful', 'user_id': user.id}), 200
    
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'success': True, 'message': 'Logout successful'}), 200

@app.route('/api/courses')
def get_courses():
    courses = Course.query.all()
    result = []
    
    for course in courses:
        result.append({
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'category': course.category,
            'language': course.language,
            'duration_weeks': course.duration_weeks
        })
    
    return jsonify({'success': True, 'courses': result}), 200

@app.route('/api/courses/<int:course_id>')
def get_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    modules = []
    for module in course.modules:
        lessons = []
        for lesson in module.lessons:
            lessons.append({
                'id': lesson.id,
                'title': lesson.title,
                'order': lesson.order
            })
            
        modules.append({
            'id': module.id,
            'title': module.title,
            'description': module.description,
            'order': module.order,
            'lessons': lessons
        })
    
    return jsonify({
        'success': True,
        'course': {
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'category': course.category,
            'language': course.language,
            'duration_weeks': course.duration_weeks,
            'modules': modules
        }
    }), 200

@app.route('/api/lessons/<int:lesson_id>')
@login_required
def get_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Record progress
    progress = Progress.query.filter_by(user_id=current_user.id, lesson_id=lesson_id).first()
    if not progress:
        progress = Progress(user_id=current_user.id, lesson_id=lesson_id, status='in-progress')
        db.session.add(progress)
    
    progress.last_accessed = datetime.utcnow()
    db.session.commit()
    
    resources = []
    for resource in lesson.resources:
        resources.append({
            'id': resource.id,
            'title': resource.title,
            'resource_type': resource.resource_type,
            'url': resource.url,
            'is_downloadable': resource.is_downloadable
        })
    
    return jsonify({
        'success': True,
        'lesson': {
            'id': lesson.id,
            'title': lesson.title,
            'content': lesson.content,
            'order': lesson.order,
            'resources': resources
        }
    }), 200

@app.route('/api/enroll', methods=['POST'])
@login_required
def enroll():
    data = request.get_json()
    course_id = data.get('course_id')
    
    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if existing_enrollment:
        return jsonify({'success': False, 'message': 'Already enrolled in this course'}), 400
    
    # Create new enrollment
    enrollment = Enrollment(user_id=current_user.id, course_id=course_id)
    
    try:
        db.session.add(enrollment)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Enrollment successful'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/user/progress')
@login_required
def get_user_progress():
    enrollments = Enrollment.query.filter_by(user_id=current_user.id).all()
    result = []
    
    for enrollment in enrollments:
        course = enrollment.course
        modules = []
        
        for module in course.modules:
            lesson_progress = []
            
            for lesson in module.lessons:
                progress = Progress.query.filter_by(
                    user_id=current_user.id,
                    lesson_id=lesson.id
                ).first()
                
                status = 'not-started'
                if progress:
                    status = progress.status
                
                lesson_progress.append({
                    'lesson_id': lesson.id,
                    'title': lesson.title,
                    'status': status
                })
            
            modules.append({
                'module_id': module.id,
                'title': module.title,
                'lessons': lesson_progress
            })
        
        result.append({
            'course_id': course.id,
            'title': course.title,
            'enrollment_date': enrollment.enrollment_date.strftime('%Y-%m-%d'),
            'modules': modules
        })
    
    return jsonify({'success': True, 'progress': result}), 200

@app.route('/api/complete-lesson', methods=['POST'])
@login_required
def complete_lesson():
    data = request.get_json()
    lesson_id = data.get('lesson_id')
    
    progress = Progress.query.filter_by(user_id=current_user.id, lesson_id=lesson_id).first()
    
    if not progress:
        progress = Progress(user_id=current_user.id, lesson_id=lesson_id)
        db.session.add(progress)
    
    progress.status = 'completed'
    progress.completion_date = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Lesson marked as completed'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Admin routes
@app.route('/api/admin/users')
@login_required
def admin_get_users():
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    users = User.query.all()
    result = []
    
    for user in users:
        result.append({
            'id': user.id,
            'name': user.name,
            'phone': user.phone,
            'location': user.location,
            'district': user.district,
            'state': user.state,
            'date_registered': user.date_registered.strftime('%Y-%m-%d'),
            'is_active': user.is_active
        })
    
    return jsonify({'success': True, 'users': result}), 200

# Main entry point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)