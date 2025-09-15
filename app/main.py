from flask import Flask, jsonify
import os

from app.config import init_database_from_env
from app.routes.user_routes import user_bp
from app.routes.user_profile_routes import user_profile_bp
from app.routes.classes_routes import classes_bp
from app.routes.class_membership_routes import class_membership_bp
from app.routes.lessons_routes import lessons_bp
from app.routes.lesson_version_routes import lesson_version_bp
from app.routes.assignments_routes import assignments_bp
from app.routes.assignment_file_routes import assignment_file_bp
from app.routes.submissions_routes import submissions_bp
from app.routes.submission_file_routes import submission_file_bp
from app.routes.files_routes import files_bp
from app.routes.grades_routes import grades_bp
from app.routes.ai_edits_routes import ai_edits_bp
from app.routes.presigned_upload_routes import presigned_upload_bp
from app.routes.notifications_routes import notifications_bp
from app.routes.audit_logs_routes import audit_logs_bp

try:
    from flasgger import Swagger
except Exception:
    Swagger = None


def create_app() -> Flask:
    init_database_from_env()
    app = Flask(__name__)

    @app.get("/")
    def index():
        return "Api Successfully Running."

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    # Mount API blueprints under /api
    app.register_blueprint(user_bp, url_prefix="/api" + (user_bp.url_prefix or ""))
    app.register_blueprint(user_profile_bp, url_prefix="/api" + (user_profile_bp.url_prefix or ""))
    app.register_blueprint(classes_bp, url_prefix="/api" + (classes_bp.url_prefix or ""))
    app.register_blueprint(class_membership_bp, url_prefix="/api" + (class_membership_bp.url_prefix or ""))
    app.register_blueprint(lessons_bp, url_prefix="/api" + (lessons_bp.url_prefix or ""))
    app.register_blueprint(lesson_version_bp, url_prefix="/api" + (lesson_version_bp.url_prefix or ""))
    app.register_blueprint(assignments_bp, url_prefix="/api" + (assignments_bp.url_prefix or ""))
    app.register_blueprint(assignment_file_bp, url_prefix="/api" + (assignment_file_bp.url_prefix or ""))
    app.register_blueprint(submissions_bp, url_prefix="/api" + (submissions_bp.url_prefix or ""))
    app.register_blueprint(submission_file_bp, url_prefix="/api" + (submission_file_bp.url_prefix or ""))
    app.register_blueprint(files_bp, url_prefix="/api" + (files_bp.url_prefix or ""))
    app.register_blueprint(grades_bp, url_prefix="/api" + (grades_bp.url_prefix or ""))
    app.register_blueprint(ai_edits_bp, url_prefix="/api" + (ai_edits_bp.url_prefix or ""))
    app.register_blueprint(presigned_upload_bp, url_prefix="/api" + (presigned_upload_bp.url_prefix or ""))
    app.register_blueprint(notifications_bp, url_prefix="/api" + (notifications_bp.url_prefix or ""))
    app.register_blueprint(audit_logs_bp, url_prefix="/api" + (audit_logs_bp.url_prefix or ""))

    # Swagger UI at /api (Swagger 2.0)
    if Swagger is not None:
        template = {
            "swagger": "2.0",
            "info": {"title": "LMS Backend API", "version": "1.0.0"},
            "basePath": "/api",
            "schemes": ["http"],
            "tags": [
                {"name": "Users", "description": "User management"},
                {"name": "UserProfiles", "description": "User profile management"},
                {"name": "Classes", "description": "Class management"},
                {"name": "ClassMemberships", "description": "Class membership management"},
                {"name": "Lessons", "description": "Lesson management"},
                {"name": "LessonVersions", "description": "Lesson versioning"},
                {"name": "Assignments", "description": "Assignment management"},
                {"name": "AssignmentFiles", "description": "Assignment-file mappings"},
                {"name": "Submissions", "description": "Submissions management"},
                {"name": "SubmissionFiles", "description": "Submission-file mappings"},
                {"name": "Files", "description": "Files metadata management"},
                {"name": "Grades", "description": "Grades management"},
                {"name": "AIedits", "description": "AI edit auditing"},
                {"name": "PresignedUploads", "description": "Presigned upload requests"},
                {"name": "Notifications", "description": "Notifications management"},
                {"name": "AuditLogs", "description": "Audit logs"},
            ],
        }
        config = {
            "headers": [],
            "specs": [
                {
                    "endpoint": "apispec_1",
                    "route": "/api/apispec_1.json",
                    "rule_filter": lambda rule: True,
                    "model_filter": lambda tag: True,
                }
            ],
            "static_url_path": "/flasgger_static",
            "swagger_ui": True,
            "specs_route": "/api/",
        }
        Swagger(app, template=template, config=config)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG", "1") == "1")
