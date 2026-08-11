from yoyo import step

__depends__ = {"20250915_12_create_grades", "20260425_01_create_lesson_submissions"}


def add_ai_grading(backend):
    cursor = backend.cursor()

    # 1) Make grades.submission_id NULLABLE (drop FK constraint first)
    cursor.execute(
        """
        SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'grades'
          AND COLUMN_NAME = 'submission_id' AND REFERENCED_TABLE_NAME IS NOT NULL
        """
    )
    row = cursor.fetchone()
    if row:
        cursor.execute(f"ALTER TABLE `grades` DROP FOREIGN KEY `{row[0]}`")
    cursor.execute("SHOW COLUMNS FROM `grades` LIKE 'submission_id'")
    col = cursor.fetchone()
    if col and col[1].find("int unsigned") >= 0 and col[2].upper() in ("NO", ""):
        cursor.execute(
            "ALTER TABLE `grades` MODIFY COLUMN `submission_id` INT UNSIGNED NULL"
        )

    # 2) Add grades.lesson_submission_id + index
    cursor.execute("SHOW COLUMNS FROM `grades` LIKE 'lesson_submission_id'")
    if not cursor.fetchone():
        cursor.execute(
            "ALTER TABLE `grades` "
            "ADD COLUMN `lesson_submission_id` INT UNSIGNED NULL AFTER `submission_id`, "
            "ADD INDEX `idx_grades_lesson_submission_id` (`lesson_submission_id`)"
        )

    # 3) Add grades.status (draft / approved / modified)
    cursor.execute("SHOW COLUMNS FROM `grades` LIKE 'status'")
    if not cursor.fetchone():
        cursor.execute(
            "ALTER TABLE `grades` "
            "ADD COLUMN `status` VARCHAR(32) NOT NULL DEFAULT 'draft' AFTER `graded_at`"
        )

    # 4) FK lesson_submission_id -> lesson_submissions
    cursor.execute(
        """
        SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'grades'
          AND COLUMN_NAME = 'lesson_submission_id' AND REFERENCED_TABLE_NAME IS NOT NULL
        """
    )
    if not cursor.fetchone():
        cursor.execute(
            "ALTER TABLE `grades` "
            "ADD CONSTRAINT `fk_grades_lesson_submission` "
            "FOREIGN KEY (`lesson_submission_id`) REFERENCES `lesson_submissions`(`id`) "
            "ON DELETE CASCADE ON UPDATE CASCADE"
        )


def remove_ai_grading(backend):
    cursor = backend.cursor()
    cursor.execute(
        """
        SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'grades'
          AND COLUMN_NAME = 'lesson_submission_id' AND REFERENCED_TABLE_NAME IS NOT NULL
        """
    )
    row = cursor.fetchone()
    if row:
        cursor.execute(f"ALTER TABLE `grades` DROP FOREIGN KEY `{row[0]}`")
    cursor.execute("SHOW COLUMNS FROM `grades` LIKE 'lesson_submission_id'")
    if cursor.fetchone():
        cursor.execute(
            "ALTER TABLE `grades` "
            "DROP INDEX `idx_grades_lesson_submission_id`, DROP COLUMN `lesson_submission_id`"
        )
    cursor.execute("SHOW COLUMNS FROM `grades` LIKE 'status'")
    if cursor.fetchone():
        cursor.execute("ALTER TABLE `grades` DROP COLUMN `status`")


steps = [
    step(add_ai_grading, remove_ai_grading),
]