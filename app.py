from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Project, Certificate
from functools import wraps
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'student_login'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('student_login'))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('student_login'))
        if current_user.is_admin:
            flash('This page is for students only.', 'error')
            return redirect(url_for('admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('student_login'))

@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        roll_number = request.form.get('roll_number')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('student_register'))
        
        if User.query.filter_by(roll_number=roll_number).first():
            flash('Roll number already registered.', 'error')
            return redirect(url_for('student_register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, email=email, roll_number=roll_number, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('student_login'))
    
    return render_template('student_register.html')

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('student_dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email, is_admin=False).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Welcome back!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('student_login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email, is_admin=True).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Welcome Admin!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'error')
    
    return render_template('admin_login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('student_login'))

@app.route('/student/dashboard')
@user_required
def student_dashboard():
    total_projects = Project.query.filter_by(user_id=current_user.id).count()
    approved_projects = Project.query.filter_by(user_id=current_user.id, status='approved').count()
    pending_projects = Project.query.filter_by(user_id=current_user.id, status='pending').count()
    
    return render_template('student_dashboard.html', 
                         total=total_projects, 
                         approved=approved_projects, 
                         pending=pending_projects)

@app.route('/student/profile', methods=['GET', 'POST'])
@user_required
def student_profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.email = request.form.get('email')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student_profile'))
    
    return render_template('student_profile.html')

@app.route('/student/upload-project', methods=['GET', 'POST'])
@user_required
def upload_project():
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        description = request.form.get('description')
        tech_stack = request.form.get('tech_stack')
        project_link = request.form.get('project_link')
        
        if not project_name or not description or not tech_stack:
            flash('Please fill all required fields.', 'error')
            return redirect(url_for('upload_project'))
        
        if len(description) < 10:
            flash('Description must be at least 10 characters.', 'error')
            return redirect(url_for('upload_project'))
        
        media_filename = None
        if 'media_file' in request.files:
            file = request.files['media_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                media_filename = f"{current_user.roll_number}_{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], media_filename))
        
        new_project = Project(
            name=project_name,
            description=description,
            tech_stack=tech_stack,
            project_link=project_link,
            media_file=media_filename,
            user_id=current_user.id,
            roll_number=current_user.roll_number
        )
        
        db.session.add(new_project)
        db.session.commit()
        
        flash('Project uploaded successfully!', 'success')
        return redirect(url_for('my_projects'))
    
    return render_template('upload_project.html')

@app.route('/student/my-projects')
@user_required
def my_projects():
    projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.created_at.desc()).all()
    return render_template('my_projects.html', projects=projects)

@app.route('/showcase')
def project_showcase():
    approved_projects = Project.query.filter_by(status='approved').order_by(Project.created_at.desc()).all()
    return render_template('project_showcase.html', projects=approved_projects)

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    pending_projects = Project.query.filter_by(status='pending').order_by(Project.created_at.desc()).all()
    total_students = User.query.filter_by(is_admin=False).count()
    total_projects = Project.query.count()
    approved_projects = Project.query.filter_by(status='approved').count()
    
    return render_template('admin_dashboard.html', 
                         pending_projects=pending_projects,
                         total_students=total_students,
                         total_projects=total_projects,
                         approved_projects=approved_projects)

@app.route('/admin/approve/<int:project_id>', methods=['POST'])
@admin_required
def approve_project(project_id):
    project = Project.query.get_or_404(project_id)
    project.status = 'approved'
    
    certificate = Certificate(
        project_id=project.id,
        student_name=project.user.name,
        project_name=project.name,
        roll_number=project.roll_number
    )
    
    db.session.add(certificate)
    db.session.commit()
    
    flash(f'Project "{project.name}" approved!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject/<int:project_id>', methods=['POST'])
@admin_required
def reject_project(project_id):
    project = Project.query.get_or_404(project_id)
    project.status = 'rejected'
    db.session.commit()
    
    flash(f'Project "{project.name}" rejected.', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/download-certificate/<int:project_id>')
@login_required
def download_certificate(project_id):
    project = Project.query.get_or_404(project_id)
    
    if project.user_id != current_user.id and not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('student_dashboard'))
    
    certificate = Certificate.query.filter_by(project_id=project_id).first()
    
    if not certificate or project.status != 'approved':
        flash('Certificate not available.', 'error')
        return redirect(url_for('my_projects'))
    
    from io import BytesIO
    from PIL import Image, ImageDraw, ImageFont
    
    img = Image.new('RGB', (1200, 800), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    draw.rectangle([(50, 50), (1150, 750)], outline=(0, 102, 204), width=5)
    
    draw.text((600, 150), "Certificate of Achievement", fill=(0, 102, 204), font=title_font, anchor="mm")
    draw.text((600, 250), "This is to certify that", fill=(0, 0, 0), font=text_font, anchor="mm")
    draw.text((600, 320), certificate.student_name, fill=(0, 102, 204), font=title_font, anchor="mm")
    draw.text((600, 400), f"Roll Number: {certificate.roll_number}", fill=(0, 0, 0), font=text_font, anchor="mm")
    draw.text((600, 460), "has successfully completed the project", fill=(0, 0, 0), font=text_font, anchor="mm")
    draw.text((600, 530), certificate.project_name, fill=(0, 102, 204), font=title_font, anchor="mm")
    draw.text((600, 630), f"Issued on: {certificate.issued_at.strftime('%B %d, %Y')}", fill=(0, 0, 0), font=text_font, anchor="mm")
    
    buffer = BytesIO()
    img.save(buffer, 'PNG')
    buffer.seek(0)
    
    return send_file(buffer, mimetype='image/png', as_attachment=True, download_name=f'certificate_{project.name}.png')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

with app.app_context():
    db.create_all()
    
    admin = User.query.filter_by(email='admin@admin.com').first()
    if not admin:
        admin_user = User(
            name='Admin',
            email='admin@admin.com',
            roll_number='ADMIN001',
            password=generate_password_hash('admin123', method='pbkdf2:sha256'),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
