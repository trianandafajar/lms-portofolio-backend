from yoyo import step

__depends__ = {"20260811_01_add_ai_grading"}


def add_block_index(backend):
    cursor = backend.cursor()
    cursor.execute("SHOW COLUMNS FROM `grades` LIKE 'block_index'")
    if not cursor.fetchone():
        cursor.execute(
            "ALTER TABLE `grades` "
            "ADD COLUMN `block_index` INT NULL AFTER `lesson_submission_id`, "
            "ADD INDEX `idx_grades_lesson_block` (`lesson_submission_id`, `block_index`)"
        )


def remove_block_index(backend):
    cursor = backend.cursor()
    cursor.execute("SHOW COLUMNS FROM `grades` LIKE 'block_index'")
    if cursor.fetchone():
        cursor.execute(
            "ALTER TABLE `grades` "
            "DROP INDEX `idx_grades_lesson_block`, DROP COLUMN `block_index`"
        )


steps = [step(add_block_index, remove_block_index)]