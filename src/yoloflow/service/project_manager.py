"""import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from ..model import Project, TaskTypect manager for handling multiple YOLOFlow projects.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from ..model import Project, TaskType


class ProjectManager:
    """
    Manages multiple YOLOFlow projects and maintains a database of project records.
    
    The project manager maintains a SQLite database with project metadata including:
    - Project name
    - Project path
    - Creation time
    - Last opened time
    - Task type
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize project manager.
        
        Args:
            db_path: Path to SQLite database file. If None, uses 'yoloflow.db' in current directory.
        """
        if db_path is None:
            db_path = Path.cwd() / "yoloflow.db"
        
        self.db_path = Path(db_path) if db_path != ":memory:" else ":memory:"
        self._conn = None  # For memory database persistence
        self._init_database()
    
    def _get_connection(self):
        """Get database connection, maintaining memory database persistence."""
        if self.db_path == ":memory:":
            if self._conn is None:
                self._conn = sqlite3.connect(":memory:")
            return self._conn
        else:
            return sqlite3.connect(self.db_path)
    
    def close(self):
        """Close any persistent database connections."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None
    
    def __enter__(self):
        """Support context manager protocol."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support context manager protocol."""
        self.close()
    
    def __len__(self):
        """Return the number of projects in the database."""
        return len(self.get_all_projects())
    
    def _init_database(self):
        """Initialize the SQLite database with required tables."""
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL UNIQUE,
                    task_type TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    last_opened_at TEXT,
                    is_favorite INTEGER DEFAULT 0
                )
            """)
            conn.commit()
        finally:
            if self.db_path != ":memory:":
                conn.close()
    
    def create_project(
        self,
        project_path: str,
        project_name: str,
        task_type: TaskType,
        description: str = ""
    ) -> Project:
        """
        Create a new project and add it to the database.
        
        Args:
            project_path: Path where to create the project
            project_name: Name of the project
            task_type: Type of the project
            description: Optional description
            
        Returns:
            Project: The created project
            
        Raises:
            FileExistsError: If project already exists
            sqlite3.IntegrityError: If project path already in database
        """
        # Create the project
        project = Project.create_new(project_path, project_name, task_type, description)
        
        # Add to database
        now = datetime.now().isoformat()
        conn = self._get_connection()
        try:
            conn.execute("""
                INSERT INTO projects (name, path, task_type, description, created_at, last_opened_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (project_name, str(project.project_path), task_type.value, description, now, now))
            conn.commit()
        finally:
            if self.db_path != ":memory:":
                conn.close()
        
        return project
    
    def open_project(self, project_path: str) -> Project:
        """
        Open an existing project and update its last opened time.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Project: The opened project
            
        Raises:
            FileNotFoundError: If project doesn't exist
            ValueError: If not a valid YOLOFlow project
        """
        project = Project(project_path)
        
        # Update last opened time in database
        now = datetime.now().isoformat()
        conn = self._get_connection()
        try:
            # Try to update existing record
            cursor = conn.execute("""
                UPDATE projects 
                SET last_opened_at = ?, name = ?, task_type = ?, description = ?
                WHERE path = ?
            """, (now, project.name, project.task_type.value, project.description, str(project.project_path)))
            
            # If no existing record, create one
            if cursor.rowcount == 0:
                conn.execute("""
                    INSERT INTO projects (name, path, task_type, description, created_at, last_opened_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (project.name, str(project.project_path), project.task_type.value, 
                     project.description, now, now))
            
            conn.commit()
        finally:
            if self.db_path != ":memory:":
                conn.close()
        
        return project
    
    def get_recent_projects(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get list of recently opened projects.
        
        Args:
            limit: Maximum number of projects to return
            
        Returns:
            List of project records
        """
        conn = self._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM projects 
                WHERE last_opened_at IS NOT NULL
                ORDER BY last_opened_at DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            if self.db_path != ":memory:":
                conn.close()
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """
        Get list of all projects in the database.
        
        Returns:
            List of all project records
        """
        conn = self._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM projects ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            if self.db_path != ":memory:":
                conn.close()
    
    def remove_project(self, project_path: str, delete_files: bool = False):
        """
        Remove project from database and optionally delete files.
        
        Args:
            project_path: Path to the project
            delete_files: If True, also delete project files
        """
        # Delete files if requested
        if delete_files:
            try:
                project = Project(project_path)
                project.delete(confirm=True)
            except Exception:
                pass  # Project might not exist or be invalid
        
        # Remove from database
        conn = self._get_connection()
        try:
            conn.execute("DELETE FROM projects WHERE path = ?", (str(Path(project_path).resolve()),))
            conn.commit()
        finally:
            if self.db_path != ":memory:":
                conn.close()
    
    def set_favorite(self, project_path: str, is_favorite: bool = True):
        """
        Mark/unmark a project as favorite.
        
        Args:
            project_path: Path to the project
            is_favorite: Whether to mark as favorite
        """
        conn = self._get_connection()
        try:
            conn.execute("""
                UPDATE projects 
                SET is_favorite = ? 
                WHERE path = ?
            """, (1 if is_favorite else 0, str(Path(project_path).resolve())))
            conn.commit()
        finally:
            if self.db_path != ":memory:":
                conn.close()
    
    def get_favorite_projects(self) -> List[Dict[str, Any]]:
        """
        Get list of favorite projects.
        
        Returns:
            List of favorite project records
        """
        conn = self._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM projects 
                WHERE is_favorite = 1 
                ORDER BY name
            """)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            if self.db_path != ":memory:":
                conn.close()
    
    def project_exists_in_db(self, project_path: str) -> bool:
        """
        Check if a project exists in the database.
        
        Args:
            project_path: Path to check
            
        Returns:
            bool: True if project exists in database
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM projects WHERE path = ?
            """, (str(Path(project_path).resolve()),))
            return cursor.fetchone()[0] > 0
        finally:
            if self.db_path != ":memory:":
                conn.close()
    
    def validate_project_paths(self) -> List[str]:
        """
        Validate all project paths in database and return list of invalid ones.
        
        Returns:
            List of invalid project paths
        """
        invalid_paths = []
        projects = self.get_all_projects()
        
        for project_record in projects:
            project_path = project_record['path']
            try:
                project = Project(project_path)
                if not project.is_valid():
                    invalid_paths.append(project_path)
            except Exception:
                invalid_paths.append(project_path)
        
        return invalid_paths
    
    def cleanup_invalid_projects(self):
        """Remove invalid project entries from database."""
        invalid_paths = self.validate_project_paths()
        
        conn = self._get_connection()
        try:
            for path in invalid_paths:
                conn.execute("DELETE FROM projects WHERE path = ?", (path,))
            conn.commit()
        finally:
            if self.db_path != ":memory:":
                conn.close()
