from marshmallow import Schema, fields

class GradeSchema(Schema):
    id = fields.Int(dump_only=True)
    submission_id = fields.Int(allow_none=True)
    lesson_submission_id = fields.Int(allow_none=True)
    grader_id = fields.Int(required=True)
    score = fields.Int(required=True)
    feedback = fields.Str(allow_none=True)
    suggested_improvement = fields.Str(allow_none=True)
    status = fields.Str(dump_default="draft")
    graded_at = fields.DateTime(dump_only=True)