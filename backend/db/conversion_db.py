import sqlite3
from core import get_settings, validate_sql_identifier
from .file_db import FileDB

class ConversionDB(FileDB):
    settings = get_settings()
    DB_PATH = settings.db_path
    TABLE_NAME = settings.conversion_table_name

    def __init__(self):
        # Validate table name on initialization to prevent SQL injection
        self.TABLE_NAME = validate_sql_identifier(self.TABLE_NAME)
        super().__init__()