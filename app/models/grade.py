from peewee import (
    Model,
    AutoField,
    IntegerField,
    CharField,
    TextField,
    DateTimeField,
    ForeignKeyField,
)
from app.db import database
from app.models.submission import Submission
from app.models.lesson_submission import LessonSubmission
from app.models.user import User

class BaseModel(Model):
    class Meta:
        database = database

class Grade(BaseModel):
    id = AutoField()
    submission = ForeignKeyField(Submission, backref='grades', null=True, on_delete='CASCADE', on_update='CASCADE', column_name='submission_id')
    lesson_submission = ForeignKeyField(LessonSubmission, backref='grades', null=True, on_delete='CASCADE', on_update='CASCADE', column_name='lesson_submission_id')
    block_index = IntegerField(null=True)
    grader = ForeignKeyField(User, backref='grades_given', on_delete='CASCADE', on_update='CASCADE', column_name='grader_id')
    score = IntegerField()
    feedback = TextField(null=True)
    status = CharField(max_length=32, default='draft')
    graded_at = DateTimeField()

    class Meta:
        table_name = "grades"
