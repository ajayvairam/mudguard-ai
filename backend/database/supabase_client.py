import os
import uuid
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from config import settings, BASE_DIR

# Determine if real Supabase keys are configured
HAS_SUPABASE = bool(
    settings.SUPABASE_URL 
    and "your-project" not in settings.SUPABASE_URL
    and settings.SUPABASE_SERVICE_ROLE_KEY
    and "your-supabase" not in settings.SUPABASE_SERVICE_ROLE_KEY
)

supabase_client = None
if HAS_SUPABASE:
    try:
        from supabase import create_client, Client
        client_instance: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        # Probe table existence to ensure migrations have been applied
        client_instance.table("prescriptions").select("id").limit(1).execute()
        supabase_client = client_instance
        print("Connected to Supabase successfully and verified tables.")
    except Exception as e:
        print(f"Notice: Supabase remote schema check ({e}). Using local SQLite database engine until supabase_schema.sql is executed in Supabase.")
        supabase_client = None

# Local SQLite Store for offline/demo operation
LOCAL_DB_PATH = BASE_DIR / "mediguard_local.db"

def init_local_db():
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    
    # Profiles
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        id TEXT PRIMARY KEY,
        user_id TEXT UNIQUE NOT NULL,
        full_name TEXT,
        email TEXT,
        avatar_url TEXT,
        preferred_language TEXT DEFAULT 'en',
        created_at TEXT,
        updated_at TEXT
    )
    """)
    
    # Prescriptions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prescriptions (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        file_url TEXT,
        file_name TEXT NOT NULL,
        file_type TEXT,
        doctor_name TEXT,
        prescription_date TEXT,
        raw_text TEXT,
        ocr_confidence REAL DEFAULT 1.0,
        status TEXT DEFAULT 'uploaded',
        created_at TEXT
    )
    """)
    
    # Medicines
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medicines (
        id TEXT PRIMARY KEY,
        prescription_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        original_name TEXT NOT NULL,
        normalized_name TEXT,
        generic_name TEXT,
        active_ingredient TEXT,
        strength TEXT,
        dosage TEXT,
        frequency TEXT,
        duration TEXT,
        route TEXT DEFAULT 'oral',
        instructions TEXT,
        confidence REAL DEFAULT 0.95,
        requires_verification INTEGER DEFAULT 0,
        created_at TEXT
    )
    """)
    
    # Medication Analysis
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medication_analysis (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        medicine_a_id TEXT,
        medicine_b_id TEXT,
        medicine_a_name TEXT,
        medicine_b_name TEXT,
        analysis_type TEXT NOT NULL,
        severity TEXT DEFAULT 'LOW',
        description TEXT NOT NULL,
        recommendation TEXT NOT NULL,
        source TEXT,
        created_at TEXT
    )
    """)
    
    # Consolidated Medications
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS consolidated_medications (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        analysis_id TEXT,
        medicine_name TEXT NOT NULL,
        generic_name TEXT,
        strength TEXT,
        dosage TEXT,
        frequency TEXT,
        duration TEXT,
        instructions TEXT,
        status TEXT DEFAULT 'active',
        requires_review INTEGER DEFAULT 0,
        review_reason TEXT,
        source_prescriptions TEXT,
        created_at TEXT
    )
    """)
    
    # Reminders
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        medicine_id TEXT,
        medicine_name TEXT NOT NULL,
        dose TEXT NOT NULL,
        time TEXT NOT NULL,
        frequency TEXT DEFAULT 'once_daily',
        start_date TEXT,
        end_date TEXT,
        instructions TEXT,
        enabled INTEGER DEFAULT 1,
        created_at TEXT
    )
    """)
    
    # Reminder History
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminder_history (
        id TEXT PRIMARY KEY,
        reminder_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        scheduled_at TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        taken_at TEXT,
        created_at TEXT
    )
    """)
    
    conn.commit()
    conn.close()

# Initialize DB structure on import
init_local_db()

class LocalQueryBuilder:
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.filters = []
        self._order_by = None
        self._limit = None

    def eq(self, column: str, value: Any):
        self.filters.append((column, "=", value))
        return self

    def order(self, column: str, desc: bool = False):
        self._order_by = (column, "DESC" if desc else "ASC")
        return self

    def limit(self, count: int):
        self._limit = count
        return self

    def execute(self):
        conn = sqlite3.connect(LOCAL_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = f"SELECT * FROM {self.table_name}"
        params = []
        if self.filters:
            clauses = [f"{col} {op} ?" for col, op, val in self.filters]
            query += " WHERE " + " AND ".join(clauses)
            params = [val for _, _, val in self.filters]
            
        if self._order_by:
            query += f" ORDER BY {self._order_by[0]} {self._order_by[1]}"
            
        if self._limit:
            query += f" LIMIT {self._limit}"
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        result_data = [dict(row) for row in rows]
        conn.close()
        
        # Parse booleans and JSON if needed
        for row in result_data:
            if "requires_verification" in row:
                row["requires_verification"] = bool(row["requires_verification"])
            if "requires_review" in row:
                row["requires_review"] = bool(row["requires_review"])
            if "enabled" in row:
                row["enabled"] = bool(row["enabled"])
            if "source_prescriptions" in row and isinstance(row["source_prescriptions"], str):
                try:
                    row["source_prescriptions"] = json.loads(row["source_prescriptions"])
                except Exception:
                    row["source_prescriptions"] = [row["source_prescriptions"]]
                    
        class Response:
            data = result_data
        return Response()

class LocalTable:
    def __init__(self, table_name: str):
        self.table_name = table_name

    def select(self, columns: str = "*"):
        return LocalQueryBuilder(self.table_name)

    def insert(self, record_or_records: Any):
        class InsertQuery:
            def __init__(query_self, table_name, records_data):
                query_self.table_name = table_name
                query_self.records_data = records_data if isinstance(records_data, list) else [records_data]

            def execute(query_self):
                conn = sqlite3.connect(LOCAL_DB_PATH)
                cursor = conn.cursor()
                inserted = []
                now_str = datetime.utcnow().isoformat()
                
                for r in query_self.records_data:
                    item = dict(r)
                    if "id" not in item or not item["id"]:
                        item["id"] = str(uuid.uuid4())
                    if "created_at" not in item or not item["created_at"]:
                        item["created_at"] = now_str
                        
                    # Serialize special types
                    for k, v in list(item.items()):
                        if isinstance(v, bool):
                            item[k] = 1 if v else 0
                        elif isinstance(v, list):
                            item[k] = json.dumps(v)
                            
                    cols = list(item.keys())
                    placeholders = ",".join(["?"] * len(cols))
                    col_str = ",".join(cols)
                    vals = [item[c] for c in cols]
                    
                    cursor.execute(f"INSERT OR REPLACE INTO {query_self.table_name} ({col_str}) VALUES ({placeholders})", vals)
                    inserted.append(item)
                    
                conn.commit()
                conn.close()
                
                class Response:
                    data = inserted
                    def execute(self):
                        return self
                return Response()

        return InsertQuery(self.table_name, record_or_records)

    def update(self, values: Dict[str, Any]):
        class UpdateQuery:
            def __init__(self, table, vals):
                self.table = table
                self.vals = dict(vals)
                self.filters = []

            def eq(self, column: str, value: Any):
                self.filters.append((column, value))
                return self

            def execute(self):
                conn = sqlite3.connect(LOCAL_DB_PATH)
                cursor = conn.cursor()
                now_str = datetime.utcnow().isoformat()
                if "updated_at" not in self.vals and self.table == "profiles":
                    self.vals["updated_at"] = now_str
                    
                set_clauses = []
                params = []
                for k, v in self.vals.items():
                    set_clauses.append(f"{k} = ?")
                    if isinstance(v, bool):
                        params.append(1 if v else 0)
                    elif isinstance(v, list):
                        params.append(json.dumps(v))
                    else:
                        params.append(v)
                        
                where_clauses = [f"{col} = ?" for col, _ in self.filters]
                params.extend([val for _, val in self.filters])
                
                query = f"UPDATE {self.table} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}"
                cursor.execute(query, params)
                conn.commit()
                conn.close()
                class Response:
                    data = [self.vals]
                return Response()

        return UpdateQuery(self.table_name, values)

    def delete(self):
        class DeleteQuery:
            def __init__(self, table):
                self.table = table
                self.filters = []

            def eq(self, column: str, value: Any):
                self.filters.append((column, value))
                return self

            def execute(self):
                conn = sqlite3.connect(LOCAL_DB_PATH)
                cursor = conn.cursor()
                where_clauses = [f"{col} = ?" for col, _ in self.filters]
                params = [val for _, val in self.filters]
                query = f"DELETE FROM {self.table} WHERE {' AND '.join(where_clauses)}"
                cursor.execute(query, params)
                conn.commit()
                conn.close()
                class Response:
                    data = []
                return Response()

        return DeleteQuery(self.table_name)

class LocalDatabase:
    def table(self, table_name: str) -> LocalTable:
        return LocalTable(table_name)

# Expose unified db accessor
def get_db():
    if supabase_client:
        return supabase_client
    return LocalDatabase()
