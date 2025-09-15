import os
import sys
import argparse
from urllib.parse import urlparse
import pymysql
from yoyo import get_backend, read_migrations
from app.config import load_env, env_db_uri
import shutil

DEFAULT_DB_URI = "mysql://root:@127.0.0.1:3306/lms"
DEFAULT_MIGRATIONS_DIR = "migrations"

def ensure_database_exists(db_uri: str) -> None:
	parsed = urlparse(db_uri)
	if parsed.scheme != 'mysql':
		return
	dbname = (parsed.path or '/').lstrip('/') or None
	if not dbname:
		return
	host = parsed.hostname or '127.0.0.1'
	port = parsed.port or 3306
	user = parsed.username or 'root'
	password = parsed.password or ''
	conn = pymysql.connect(host=host, port=port, user=user, password=password, charset='utf8mb4', autocommit=True)
	try:
		with conn.cursor() as cur:
			cur.execute(
				f"CREATE DATABASE IF NOT EXISTS `{dbname}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
			)
	finally:
		conn.close()

def cmd_migrate(db_uri: str, migrations_dir: str) -> int:
	ensure_database_exists(db_uri)
	backend = get_backend(db_uri)
	migrations = read_migrations(migrations_dir)
	with backend.lock():
		pending = backend.to_apply(migrations)
		if not pending:
			print("No migrations to apply.")
			return 0
		backend.apply_migrations(pending)
		print(f"Applied {len(pending)} migration(s).")
		return 0

def cmd_serve() -> int:
	load_env()
	from app.main import create_app
	app = create_app()
	host = os.getenv("FLASK_HOST", "0.0.0.0")
	port = int(os.getenv("PORT", os.getenv("FLASK_PORT", "5000")))
	debug = os.getenv("FLASK_DEBUG", "1") == "1"
	app.run(host=host, port=port, debug=debug)
	return 0

def cmd_cache_clear() -> int:
	project_root = os.path.dirname(os.path.abspath(__file__))
	removed_dirs = 0
	removed_files = 0
	for current_dir, dirnames, filenames in os.walk(project_root):
		if "__pycache__" in dirnames:
			cache_dir = os.path.join(current_dir, "__pycache__")
			try:
				shutil.rmtree(cache_dir, ignore_errors=True)
				removed_dirs += 1
			except Exception:
				pass
		for fname in list(filenames):
			if fname.endswith(".pyc"):
				fpath = os.path.join(current_dir, fname)
				try:
					os.remove(fpath)
					removed_files += 1
				except Exception:
					pass
	print(f"Cleared {removed_dirs} __pycache__ folder(s) and {removed_files} .pyc file(s).")
	return 0

def main() -> int:
	load_env()

	parser = argparse.ArgumentParser(prog="run.py", description="Project runner")
	sub = parser.add_subparsers(dest="command")

	sub.add_parser("migrate", help="Auto-create DB (MySQL) and apply yoyo migrations")
	sub.add_parser("serve", help="Run Flask development server")
	sub.add_parser("cache:clear", help="Remove all __pycache__ folders and .pyc files")

	args = parser.parse_args()
	if args.command == "migrate":
		db_uri = env_db_uri()
		migrations_dir = os.getenv("MIGRATIONS_DIR", DEFAULT_MIGRATIONS_DIR)
		return cmd_migrate(db_uri, migrations_dir)
	elif args.command == "serve":
		return cmd_serve()
	elif args.command == "cache:clear":
		return cmd_cache_clear()

	parser.print_help()
	return 1

if __name__ == "__main__":
	sys.exit(main())
