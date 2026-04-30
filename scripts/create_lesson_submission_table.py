from app.config import init_database_from_env
from app.db import database
from app.models.lesson_submission import LessonSubmission

def create_table():
    init_database_from_env()
    if database.is_closed():
        database.connect()
    
    database.create_tables([LessonSubmission])
    print("✅ Table 'lesson_submissions' created successfully!")
    
    if not database.is_closed():
        database.close()

if __name__ == "__main__":
    create_table()
