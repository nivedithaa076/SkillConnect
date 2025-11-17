# Student Project Management Platform

## Overview
A comprehensive web application for managing student project submissions with separate admin and student portals. Built with Flask, this platform allows students to upload projects, track their status, and download certificates for approved work. Administrators can review, approve, or reject submissions.

## Project Status
**Current State:** Fully functional MVP with all core features implemented
**Last Updated:** October 28, 2025

## Tech Stack
- **Backend:** Python 3.11, Flask 3.1.2
- **Database:** SQLite (SQLAlchemy ORM)
- **Authentication:** Flask-Login with password hashing (Werkzeug)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **File Handling:** Pillow (image processing for certificates)

## Features Implemented

### Authentication System
- Student registration with email and roll number validation
- Separate login pages for students and administrators
- Role-based access control with decorators (@admin_required, @user_required)
- Session management with Flask-Login
- Password hashing using Werkzeug's pbkdf2:sha256

### Student Portal
1. **Dashboard**
   - Statistics display (total, approved, pending projects)
   - Quick action cards for uploading projects and viewing showcase
   - Personalized welcome message

2. **User Profile**
   - View and edit name, email
   - Roll number displayed (read-only)
   - Profile update functionality

3. **Upload Project**
   - Form with validation for all required fields
   - Support for multiple file types (JPG, PNG, GIF, MP4, AVI, MOV, PDF)
   - Maximum file size: 16MB
   - Optional project link (GitHub/demo URL)
   - Auto-populated roll number from user profile

4. **My Projects**
   - Card grid layout of all user's projects
   - Color-coded status badges (Approved, Pending, Rejected)
   - Project details: name, description, tech stack, submission date
   - Media preview for images
   - Download certificate button (for approved projects)

5. **Project Showcase**
   - Public gallery of all approved projects
   - Responsive grid layout (3 columns desktop, 2 tablet, 1 mobile)
   - Project thumbnails with hover effects
   - Links to external project URLs

### Admin Portal
1. **Dashboard**
   - System statistics (students, projects, approved count)
   - Pending projects review queue
   - Project approval/rejection workflow

2. **Project Review**
   - Detailed view of pending project submissions
   - One-click approve/reject actions
   - Automatic certificate generation on approval

3. **Certificate Generation**
   - Dynamic certificate creation using Pillow
   - Personalized with student name, roll number, project name
   - Professional design with branding
   - PNG format download

## Project Structure
```
├── app.py                    # Main Flask application
├── models.py                 # Database models (User, Project, Certificate)
├── templates/                # HTML templates
│   ├── base.html            # Base template with navigation
│   ├── student_login.html   # Student login page
│   ├── student_register.html# Student registration
│   ├── admin_login.html     # Admin login page
│   ├── student_dashboard.html# Student dashboard
│   ├── student_profile.html # Student profile page
│   ├── upload_project.html  # Project upload form
│   ├── my_projects.html     # User's projects list
│   ├── project_showcase.html# Public showcase
│   └── admin_dashboard.html # Admin review page
├── static/
│   └── css/
│       └── style.css        # Application styling
├── uploads/                 # User-uploaded files
├── database.db              # SQLite database
└── replit.md               # This file

```

## Database Schema

### Users Table
- id (Primary Key)
- name (String, 200)
- email (String, 200, Unique)
- roll_number (String, 50, Unique)
- password (Hashed String, 200)
- is_admin (Boolean, default: False)
- created_at (DateTime)

### Projects Table
- id (Primary Key)
- name (String, 200)
- description (Text)
- tech_stack (String, 500)
- project_link (String, 500, Optional)
- media_file (String, 500, Optional)
- roll_number (String, 50)
- status (String, 20: 'pending', 'approved', 'rejected')
- user_id (Foreign Key → Users)
- created_at (DateTime)

### Certificates Table
- id (Primary Key)
- project_id (Foreign Key → Projects)
- student_name (String, 200)
- project_name (String, 200)
- roll_number (String, 50)
- issued_at (DateTime)

## Default Credentials

### Admin Account
- **Email:** admin@admin.com
- **Password:** admin123

*Note: This is automatically created on first run. Change credentials in production.*

## Running the Application
The Flask server runs on port 5000 and is configured to accept connections from all hosts (0.0.0.0) for Replit deployment.

## Security Features
- Password hashing with pbkdf2:sha256
- Session-based authentication
- Role-based access control
- File upload validation
- CSRF protection via Flask sessions
- Secure filename handling

## Responsive Design
The application is fully responsive with breakpoints for:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (< 768px)

## Recent Changes
- **Oct 28, 2025:** Initial project setup with all core features
- Database models created with proper relationships
- Authentication system implemented
- Student and admin portals completed
- Certificate generation system added
- Responsive UI design implemented

## Future Enhancements (Not Implemented)
- Project editing and deletion for students
- Admin feedback/comments on rejected projects
- Advanced search and filtering in showcase
- Email notifications for approval/rejection
- Custom certificate templates
- Project categories/tags
- Bulk approval actions
- Analytics dashboard
- Export project data to CSV/PDF

## Environment Variables
- `SESSION_SECRET`: Flask session secret key (defaults to dev key if not set)

## Dependencies
See pyproject.toml for complete list. Key dependencies:
- flask==3.1.2
- flask-login==0.6.3
- flask-sqlalchemy==3.1.1
- werkzeug==3.1.3
- pillow==12.0.0
