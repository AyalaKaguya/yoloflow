"""
Project manager for YOLOFlow.
Manages all projects using SQLite database for persistence.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from .project import Project


class ProjectManager:
    """
    项目管理器类。
    使用SQLite数据库管理所有项目的记录，包括项目名称、路径、创建时间、最后打开时间等。
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        初始化项目管理器。
        
        Args:
            db_path: 数据库文件路径，默认为当前目录下的yoloflow.db
        """
        if db_path is None:
            db_path = Path.cwd() / "yoloflow.db"
        
        self.db_path = Path(db_path)
        self._init_database()
    
    def _init_database(self) -> None:
        """初始化数据库，创建项目表。"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL UNIQUE,
                    task_type TEXT NOT NULL DEFAULT 'detect',
                    created_at TEXT NOT NULL,
                    last_opened_at TEXT,
                    description TEXT DEFAULT ''
                )
            """)
            conn.commit()
    
    def create_project(self, project_path: Path, project_name: str, task_type: str = "detect") -> Project:
        """
        创建新项目。
        
        Args:
            project_path: 项目目录路径
            project_name: 项目名称
            task_type: 任务类型
        
        Returns:
            创建的Project实例
        
        Raises:
            ValueError: 如果项目路径已存在
        """
        project_path = Path(project_path).resolve()
        
        # 检查项目是否已存在
        if self.get_project_by_path(project_path) is not None:
            raise ValueError(f"Project already exists at {project_path}")
        
        # 创建项目
        project = Project.create_new(project_path, project_name, task_type)
        
        # 添加到数据库
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO projects (name, path, task_type, created_at, last_opened_at)
                VALUES (?, ?, ?, ?, ?)
            """, (project_name, str(project_path), task_type, now, now))
            conn.commit()
        
        return project
    
    def open_project(self, project_path: Path) -> Optional[Project]:
        """
        打开现有项目。
        
        Args:
            project_path: 项目目录路径
        
        Returns:
            Project实例，如果项目不存在则返回None
        """
        project_path = Path(project_path).resolve()
        
        try:
            project = Project(project_path)
            
            # 更新最后打开时间
            self._update_last_opened(project_path)
            
            # 如果数据库中没有此项目记录，添加它
            if self.get_project_by_path(project_path) is None:
                self._add_existing_project(project)
            
            return project
        except (ValueError, FileNotFoundError):
            return None
    
    def _add_existing_project(self, project: Project) -> None:
        """将现有项目添加到数据库。"""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO projects (name, path, task_type, created_at, last_opened_at)
                VALUES (?, ?, ?, ?, ?)
            """, (project.name, str(project.path), project.task_type, now, now))
            conn.commit()
    
    def _update_last_opened(self, project_path: Path) -> None:
        """更新项目的最后打开时间。"""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE projects SET last_opened_at = ? WHERE path = ?
            """, (now, str(project_path)))
            conn.commit()
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """
        获取所有项目的信息。
        
        Returns:
            项目信息列表
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # 返回字典形式的行
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM projects ORDER BY last_opened_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_projects(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近打开的项目。
        
        Args:
            limit: 返回项目数量限制
        
        Returns:
            最近项目信息列表
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM projects 
                WHERE last_opened_at IS NOT NULL 
                ORDER BY last_opened_at DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_project_by_path(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """
        根据路径获取项目信息。
        
        Args:
            project_path: 项目路径
        
        Returns:
            项目信息字典，如果不存在则返回None
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM projects WHERE path = ?
            """, (str(project_path),))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def remove_project_record(self, project_path: Path) -> bool:
        """
        从数据库中移除项目记录（不删除文件）。
        
        Args:
            project_path: 项目路径
        
        Returns:
            是否成功移除
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM projects WHERE path = ?
            """, (str(project_path),))
            conn.commit()
            return cursor.rowcount > 0
    
    def update_project_info(self, project_path: Path, **kwargs) -> bool:
        """
        更新项目信息。
        
        Args:
            project_path: 项目路径
            **kwargs: 要更新的字段
        
        Returns:
            是否成功更新
        """
        if not kwargs:
            return False
        
        # 构建UPDATE语句
        fields = []
        values = []
        for key, value in kwargs.items():
            if key in ['name', 'task_type', 'description']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            return False
        
        values.append(str(project_path))
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE projects SET {', '.join(fields)} WHERE path = ?
            """, values)
            conn.commit()
            return cursor.rowcount > 0
    
    def get_project_count(self) -> int:
        """获取项目总数。"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM projects")
            return cursor.fetchone()[0]
