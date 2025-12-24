"""
Database Module for Singapore Transport Intelligence

Manages SQLite database for storing historical bus arrival data,
predictions, and alert history.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

DATABASE_FILE = "transport_intelligence.db"


class TransportDatabase:
    """SQLite database manager for transport data"""

    def __init__(self, db_file: str = DATABASE_FILE):
        """Initialize database connection"""
        self.db_file = db_file
        self.conn = None
        self.init_database()

    def init_database(self):
        """Create database tables if they don't exist"""
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries

        cursor = self.conn.cursor()

        # Table: Historical bus arrivals
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bus_arrivals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bus_stop_code TEXT NOT NULL,
                bus_number TEXT NOT NULL,
                estimated_arrival TIMESTAMP NOT NULL,
                load_status TEXT NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                delay_minutes REAL,
                INDEX idx_bus_stop (bus_stop_code),
                INDEX idx_recorded_at (recorded_at),
                INDEX idx_bus_number (bus_number)
            )
        """)

        # Table: Delay predictions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS delay_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bus_stop_code TEXT NOT NULL,
                bus_number TEXT NOT NULL,
                predicted_delay REAL NOT NULL,
                confidence REAL NOT NULL,
                prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actual_delay REAL,
                INDEX idx_prediction_time (prediction_time)
            )
        """)

        # Table: Congestion alerts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS congestion_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                bus_stop_code TEXT,
                bus_number TEXT,
                message TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                notification_sent BOOLEAN DEFAULT 0,
                INDEX idx_created_at (created_at),
                INDEX idx_severity (severity)
            )
        """)

        # Table: Historical statistics (hourly aggregates)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hourly_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hour_timestamp TIMESTAMP NOT NULL,
                total_buses INTEGER NOT NULL,
                avg_delay REAL,
                severe_delays INTEGER,
                sea_count INTEGER,
                sda_count INTEGER,
                lsd_count INTEGER,
                UNIQUE(hour_timestamp)
            )
        """)

        self.conn.commit()
        print(f"✓ Database initialized: {self.db_file}")

    def insert_bus_arrival(self, arrival_data: Dict) -> int:
        """
        Insert bus arrival record

        Args:
            arrival_data: Dict with keys: bus_stop_code, bus_number,
                         estimated_arrival, load_status, delay_minutes (optional)

        Returns:
            int: ID of inserted record
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO bus_arrivals
            (bus_stop_code, bus_number, estimated_arrival, load_status, delay_minutes)
            VALUES (?, ?, ?, ?, ?)
        """, (
            arrival_data['bus_stop_code'],
            arrival_data['bus_number'],
            arrival_data['estimated_arrival'],
            arrival_data['load_status'],
            arrival_data.get('delay_minutes')
        ))
        self.conn.commit()
        return cursor.lastrowid

    def bulk_insert_arrivals(self, arrivals: List[Dict]) -> int:
        """Bulk insert multiple arrival records"""
        cursor = self.conn.cursor()
        data = [
            (a['bus_stop_code'], a['bus_number'], a['estimated_arrival'],
             a['load_status'], a.get('delay_minutes'))
            for a in arrivals
        ]
        cursor.executemany("""
            INSERT INTO bus_arrivals
            (bus_stop_code, bus_number, estimated_arrival, load_status, delay_minutes)
            VALUES (?, ?, ?, ?, ?)
        """, data)
        self.conn.commit()
        return cursor.rowcount

    def get_historical_arrivals(self, bus_stop_code: str = None,
                                bus_number: str = None,
                                days: int = 7) -> List[Dict]:
        """
        Get historical arrival data

        Args:
            bus_stop_code: Filter by bus stop (optional)
            bus_number: Filter by bus number (optional)
            days: Number of days to look back

        Returns:
            List of arrival records
        """
        cursor = self.conn.cursor()
        query = """
            SELECT * FROM bus_arrivals
            WHERE recorded_at >= datetime('now', '-' || ? || ' days')
        """
        params = [days]

        if bus_stop_code:
            query += " AND bus_stop_code = ?"
            params.append(bus_stop_code)

        if bus_number:
            query += " AND bus_number = ?"
            params.append(bus_number)

        query += " ORDER BY recorded_at DESC"

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def insert_alert(self, alert_data: Dict) -> int:
        """Insert congestion alert"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO congestion_alerts
            (alert_type, severity, bus_stop_code, bus_number, message, details)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            alert_data['alert_type'],
            alert_data['severity'],
            alert_data.get('bus_stop_code'),
            alert_data.get('bus_number'),
            alert_data['message'],
            json.dumps(alert_data.get('details', {}))
        ))
        self.conn.commit()
        return cursor.lastrowid

    def get_active_alerts(self, severity: str = None) -> List[Dict]:
        """Get unresolved alerts"""
        cursor = self.conn.cursor()
        query = """
            SELECT * FROM congestion_alerts
            WHERE resolved_at IS NULL
        """
        params = []

        if severity:
            query += " AND severity = ?"
            params.append(severity)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        alerts = [dict(row) for row in cursor.fetchall()]

        # Parse JSON details
        for alert in alerts:
            if alert['details']:
                alert['details'] = json.loads(alert['details'])

        return alerts

    def mark_alert_notified(self, alert_id: int):
        """Mark alert as notification sent"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE congestion_alerts
            SET notification_sent = 1
            WHERE id = ?
        """, (alert_id,))
        self.conn.commit()

    def resolve_alert(self, alert_id: int):
        """Mark alert as resolved"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE congestion_alerts
            SET resolved_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (alert_id,))
        self.conn.commit()

    def get_hourly_statistics(self, hours: int = 24) -> List[Dict]:
        """Get hourly statistics for trend analysis"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM hourly_statistics
            WHERE hour_timestamp >= datetime('now', '-' || ? || ' hours')
            ORDER BY hour_timestamp ASC
        """, (hours,))
        return [dict(row) for row in cursor.fetchall()]

    def calculate_hourly_stats(self):
        """Calculate and store hourly statistics from raw data"""
        cursor = self.conn.cursor()

        # Get the last hour's timestamp (rounded down)
        cursor.execute("""
            SELECT datetime(
                strftime('%Y-%m-%d %H:00:00',
                datetime('now', '-1 hour'))
            ) as hour_start
        """)
        hour_start = cursor.fetchone()[0]

        # Calculate statistics for that hour
        cursor.execute("""
            SELECT
                COUNT(*) as total_buses,
                AVG(delay_minutes) as avg_delay,
                SUM(CASE WHEN delay_minutes > 10 THEN 1 ELSE 0 END) as severe_delays,
                SUM(CASE WHEN load_status = 'SEA' THEN 1 ELSE 0 END) as sea_count,
                SUM(CASE WHEN load_status = 'SDA' THEN 1 ELSE 0 END) as sda_count,
                SUM(CASE WHEN load_status = 'LSD' THEN 1 ELSE 0 END) as lsd_count
            FROM bus_arrivals
            WHERE recorded_at >= ?
                AND recorded_at < datetime(?, '+1 hour')
        """, (hour_start, hour_start))

        stats = cursor.fetchone()

        if stats and stats['total_buses'] > 0:
            # Insert or update statistics
            cursor.execute("""
                INSERT OR REPLACE INTO hourly_statistics
                (hour_timestamp, total_buses, avg_delay, severe_delays,
                 sea_count, sda_count, lsd_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (hour_start, *stats))
            self.conn.commit()
            return dict(stats)

        return None

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✓ Database connection closed")


# Singleton instance
_db_instance = None


def get_database() -> TransportDatabase:
    """Get singleton database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = TransportDatabase()
    return _db_instance


if __name__ == "__main__":
    # Test database creation
    print("Testing database initialization...")
    db = get_database()
    print("✓ Database test successful!")
    db.close()
