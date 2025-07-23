"""
Mission History and Analytics Module
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import sqlite3
from contextlib import contextmanager

class MissionHistory:
    def __init__(self, db_path: str = "hub/missions.db"):
        """Initialize mission history with SQLite database"""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        with self._get_db() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS missions (
                    mission_id TEXT PRIMARY KEY,
                    workflow TEXT NOT NULL,
                    mission_text TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    total_duration_seconds REAL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mission_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    duration_seconds REAL,
                    result_path TEXT,
                    error_message TEXT,
                    FOREIGN KEY (mission_id) REFERENCES missions(mission_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mission_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mission_id TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    level TEXT NOT NULL,
                    component TEXT NOT NULL,
                    message TEXT NOT NULL,
                    FOREIGN KEY (mission_id) REFERENCES missions(mission_id)
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_missions_created ON missions(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_executions_mission ON agent_executions(mission_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_logs_mission ON mission_logs(mission_id)")
    
    @contextmanager
    def _get_db(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
    
    def record_mission_created(self, mission_id: str, workflow: List[Dict], mission_text: str):
        """Record new mission creation"""
        with self._get_db() as conn:
            conn.execute("""
                INSERT INTO missions (mission_id, workflow, mission_text, status, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                mission_id,
                json.dumps(workflow),
                mission_text,
                'registered',
                datetime.now().isoformat()
            ))
        
        self.add_log(mission_id, "INFO", "Hub", f"Mission {mission_id} registered")
    
    def record_mission_started(self, mission_id: str):
        """Record mission execution start"""
        with self._get_db() as conn:
            conn.execute("""
                UPDATE missions 
                SET status = 'running', started_at = ?
                WHERE mission_id = ?
            """, (datetime.now().isoformat(), mission_id))
        
        self.add_log(mission_id, "INFO", "Hub", "Mission execution started")
    
    def record_mission_completed(self, mission_id: str, status: str):
        """Record mission completion"""
        completed_at = datetime.now()
        
        with self._get_db() as conn:
            # Get start time
            result = conn.execute(
                "SELECT started_at FROM missions WHERE mission_id = ?", 
                (mission_id,)
            ).fetchone()
            
            if result and result['started_at']:
                started_at = datetime.fromisoformat(result['started_at'])
                duration = (completed_at - started_at).total_seconds()
            else:
                duration = None
            
            conn.execute("""
                UPDATE missions 
                SET status = ?, completed_at = ?, total_duration_seconds = ?
                WHERE mission_id = ?
            """, (status, completed_at.isoformat(), duration, mission_id))
        
        self.add_log(mission_id, "INFO", "Hub", f"Mission completed with status: {status}")
    
    def record_agent_execution(self, mission_id: str, agent_name: str, 
                             status: str, started_at: datetime, 
                             completed_at: Optional[datetime] = None,
                             result_path: Optional[str] = None,
                             error_message: Optional[str] = None):
        """Record agent execution details"""
        duration = None
        if completed_at:
            duration = (completed_at - started_at).total_seconds()
        
        with self._get_db() as conn:
            conn.execute("""
                INSERT INTO agent_executions 
                (mission_id, agent_name, status, started_at, completed_at, 
                 duration_seconds, result_path, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mission_id, agent_name, status, started_at.isoformat(),
                completed_at.isoformat() if completed_at else None,
                duration, result_path, error_message
            ))
        
        self.add_log(mission_id, "INFO", agent_name, 
                    f"Agent execution completed with status: {status}")
    
    def add_log(self, mission_id: str, level: str, component: str, message: str):
        """Add a log entry for a mission"""
        with self._get_db() as conn:
            conn.execute("""
                INSERT INTO mission_logs (mission_id, timestamp, level, component, message)
                VALUES (?, ?, ?, ?, ?)
            """, (mission_id, datetime.now().isoformat(), level, component, message))
    
    def get_mission_history(self, mission_id: str) -> Dict[str, Any]:
        """Get complete history for a mission"""
        with self._get_db() as conn:
            # Get mission details
            mission = conn.execute(
                "SELECT * FROM missions WHERE mission_id = ?", 
                (mission_id,)
            ).fetchone()
            
            if not mission:
                return None
            
            # Get agent executions
            agents = conn.execute(
                "SELECT * FROM agent_executions WHERE mission_id = ? ORDER BY started_at",
                (mission_id,)
            ).fetchall()
            
            # Get logs
            logs = conn.execute(
                "SELECT * FROM mission_logs WHERE mission_id = ? ORDER BY timestamp",
                (mission_id,)
            ).fetchall()
            
            return {
                "mission": dict(mission),
                "workflow": json.loads(mission['workflow']),
                "agent_executions": [dict(a) for a in agents],
                "logs": [dict(l) for l in logs]
            }
    
    def get_mission_stats(self, limit: int = 100) -> Dict[str, Any]:
        """Get mission statistics"""
        with self._get_db() as conn:
            # Overall stats
            stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_missions,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                    COUNT(CASE WHEN status = 'running' THEN 1 END) as running,
                    AVG(CASE WHEN status = 'completed' THEN total_duration_seconds END) as avg_duration
                FROM missions
            """).fetchone()
            
            # Agent performance
            agent_stats = conn.execute("""
                SELECT 
                    agent_name,
                    COUNT(*) as total_executions,
                    COUNT(CASE WHEN status = 'success' THEN 1 END) as successful,
                    AVG(duration_seconds) as avg_duration
                FROM agent_executions
                GROUP BY agent_name
            """).fetchall()
            
            # Recent missions
            recent = conn.execute("""
                SELECT mission_id, mission_text, status, created_at, total_duration_seconds
                FROM missions
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,)).fetchall()
            
            return {
                "overall": dict(stats),
                "by_agent": [dict(a) for a in agent_stats],
                "recent_missions": [dict(m) for m in recent]
            }
    
    def export_mission_report(self, mission_id: str, output_path: str):
        """Export detailed mission report"""
        history = self.get_mission_history(mission_id)
        
        if not history:
            raise ValueError(f"Mission {mission_id} not found")
        
        report = f"""# Mission Report: {mission_id}

## Overview
- **Status**: {history['mission']['status']}
- **Created**: {history['mission']['created_at']}
- **Started**: {history['mission']['started_at'] or 'N/A'}
- **Completed**: {history['mission']['completed_at'] or 'N/A'}
- **Duration**: {history['mission']['total_duration_seconds'] or 'N/A'} seconds

## Mission
{history['mission']['mission_text']}

## Workflow
```mermaid
graph TD
"""
        
        # Add workflow to report
        for edge in history['workflow']:
            report += f"    {edge['from']} --> {edge['to']}\n"
        
        report += "```\n\n## Agent Executions\n"
        
        # Add agent execution details
        for agent in history['agent_executions']:
            report += f"""
### {agent['agent_name']}
- **Status**: {agent['status']}
- **Started**: {agent['started_at']}
- **Duration**: {agent['duration_seconds'] or 'N/A'} seconds
"""
            if agent['error_message']:
                report += f"- **Error**: {agent['error_message']}\n"
            if agent['result_path']:
                report += f"- **Result**: {agent['result_path']}\n"
        
        # Add logs
        report += "\n## Execution Logs\n```\n"
        for log in history['logs']:
            report += f"[{log['timestamp']}] {log['level']} - {log['component']}: {log['message']}\n"
        report += "```\n"
        
        # Save report
        Path(output_path).write_text(report)
        return output_path