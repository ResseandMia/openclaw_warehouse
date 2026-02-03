#!/usr/bin/env python3
"""
17TRACK Package Tracking Skill
"""

import json
import sys
import os
import argparse
import sqlite3
import requests
import time
from typing import Dict, List, Optional
from datetime import datetime
try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Warning: Flask not installed. Webhook server disabled.")


class Track17:
    """17TRACK package tracking client"""
    
    def __init__(self, api_key: str = None, api_url: str = None,
                 data_dir: str = "./data"):
        self.api_key = api_key or os.environ.get("TRACK17_API_KEY")
        self.api_url = api_url or os.environ.get(
            "TRACK17_API_URL", "https://api.17track.net/v2"
        )
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, "track17.db")
        
        os.makedirs(data_dir, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracking_number TEXT UNIQUE NOT NULL,
                carrier TEXT,
                status TEXT,
                last_update TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                package_id INTEGER,
                timestamp TIMESTAMP,
                location TEXT,
                description TEXT,
                FOREIGN KEY (package_id) REFERENCES packages(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _get_db(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _request(self, endpoint: str, data: dict = None) -> dict:
        """Make API request"""
        headers = {
            "APIKey": self.api_key,
            "Content-Type": "application/json"
        }
        url = f"{self.api_url}/{endpoint}"
        
        try:
            if data:
                resp = requests.post(url, headers=headers, json=data, timeout=10)
            else:
                resp = requests.get(url, headers=headers, timeout=10)
            
            return resp.json()
            
        except Exception as e:
            return {"error": str(e)}
    
    # Package management
    def add(self, tracking_number: str, carrier: str = None) -> Dict:
        """Add a package to track"""
        conn = self._get_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO packages (tracking_number, carrier, status) VALUES (?, ?, ?)",
                (tracking_number, carrier, "pending")
            )
            conn.commit()
            
            return {
                "success": True,
                "tracking_number": tracking_number,
                "carrier": carrier,
                "message": "Package added successfully"
            }
        except sqlite3.IntegrityError:
            return {"success": False, "error": "Package already exists"}
        finally:
            conn.close()
    
    def list(self, status: str = "all") -> Dict:
        """List all packages"""
        conn = self._get_db()
        cursor = conn.cursor()
        
        query = "SELECT * FROM packages"
        if status != "all":
            query += f" WHERE status = '{status}'"
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query)
        packages = []
        
        for row in cursor.fetchall():
            packages.append({
                "id": row["id"],
                "tracking_number": row["tracking_number"],
                "carrier": row["carrier"],
                "status": row["status"],
                "last_update": row["last_update"],
                "created_at": row["created_at"]
            })
        
        conn.close()
        
        return {
            "success": True,
            "count": len(packages),
            "status_filter": status,
            "packages": packages
        }
    
    def get(self, tracking_number: str) -> Dict:
        """Get package details with events"""
        conn = self._get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM packages WHERE tracking_number = ?",
            (tracking_number,)
        )
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {"success": False, "error": "Package not found"}
        
        # Get events
        cursor.execute(
            "SELECT * FROM events WHERE package_id = ? ORDER BY timestamp DESC",
            (row["id"],)
        )
        events = []
        for e in cursor.fetchall():
            events.append({
                "timestamp": e["timestamp"],
                "location": e["location"],
                "description": e["description"]
            })
        
        conn.close()
        
        return {
            "success": True,
            "data": {
                "tracking_number": row["tracking_number"],
                "carrier": row["carrier"],
                "status": row["status"],
                "last_update": row["last_update"],
                "events": events
            }
        }
    
    def delete(self, tracking_number: str) -> Dict:
        """Delete a package"""
        conn = self._get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM events WHERE package_id IN (SELECT id FROM packages WHERE tracking_number = ?)",
            (tracking_number,)
        )
        cursor.execute(
            "DELETE FROM packages WHERE tracking_number = ?",
            (tracking_number,)
        )
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "tracking_number": tracking_number,
            "message": "Package deleted"
        }
    
    # Sync methods
    def sync(self, tracking_number: str = None) -> Dict:
        """Sync package(s) with 17TRACK API"""
        conn = self._get_db()
        cursor = conn.cursor()
        
        if tracking_number:
            # Sync single package
            cursor.execute(
                "SELECT * FROM packages WHERE tracking_number = ?",
                (tracking_number,)
            )
        else:
            # Sync all packages
            cursor.execute("SELECT * FROM packages")
        
        packages = cursor.fetchall()
        
        if not packages:
            conn.close()
            return {"success": False, "error": "No packages to sync"}
        
        # Build batch request
        numbers = [p["tracking_number"] for p in packages]
        data = {"number": numbers}
        
        result = self._request("getpackageinfo", data)
        
        if "error" in result:
            conn.close()
            return {"success": False, "error": result["error"]}
        
        # Update local database
        updated = 0
        for tracking_number, info in result.get("data", {}).items():
            status = info.get("status", "unknown")
            last_update = datetime.now().isoformat()
            
            # Update package
            cursor.execute(
                "UPDATE packages SET status = ?, last_update = ? WHERE tracking_number = ?",
                (status, last_update, tracking_number)
            )
            
            # Get package ID
            cursor.execute(
                "SELECT id FROM packages WHERE tracking_number = ?",
                (tracking_number,)
            )
            pkg_id = cursor.fetchone()["id"]
            
            # Add new events
            for event in info.get("events", []):
                cursor.execute(
                    "INSERT INTO events (package_id, timestamp, location, description) VALUES (?, ?, ?, ?)",
                    (pkg_id, event.get("time"), event.get("location"), event.get("description"))
                )
            
            updated += 1
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "synced": updated,
            "message": f"Synced {updated} packages"
        }
    
    # Import/Export
    def import_packages(self, file_path: str) -> Dict:
        """Import packages from CSV/JSON"""
        conn = self._get_db()
        cursor = conn.cursor()
        
        imported = 0
        errors = []
        
        if file_path.endswith(".json"):
            with open(file_path) as f:
                packages = json.load(f)
                for pkg in packages:
                    try:
                        cursor.execute(
                            "INSERT OR IGNORE INTO packages (tracking_number, carrier) VALUES (?, ?)",
                            (pkg.get("number"), pkg.get("carrier"))
                        )
                        imported += 1
                    except Exception as e:
                        errors.append(str(e))
        
        elif file_path.endswith(".csv"):
            import csv
            with open(file_path) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        cursor.execute(
                            "INSERT OR IGNORE INTO packages (tracking_number, carrier) VALUES (?, ?)",
                            (row.get("number", row.get("tracking_number")), row.get("carrier"))
                        )
                        imported += 1
                    except Exception as e:
                        errors.append(str(e))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "imported": imported,
            "errors": errors
        }
    
    def export_packages(self, output_file: str = None) -> Dict:
        """Export packages to JSON"""
        result = self.list()
        packages = result.get("packages", [])
        
        export_data = []
        for pkg in packages:
            details = self.get(pkg["tracking_number"])
            if details["success"]:
                export_data.append(details["data"])
        
        if output_file:
            with open(output_file, "w") as f:
                json.dump(export_data, f, indent=2)
        
        return {
            "success": True,
            "count": len(export_data),
            "data": export_data
        }
    
    # Webhook
    def handle_webhook(self, data: dict) -> Dict:
        """Handle webhook notification"""
        tracking_number = data.get("tracking_number")
        new_status = data.get("status")
        events = data.get("events", [])
        
        conn = self._get_db()
        cursor = conn.cursor()
        
        # Update status
        cursor.execute(
            "UPDATE packages SET status = ?, last_update = ? WHERE tracking_number = ?",
            (new_status, datetime.now().isoformat(), tracking_number)
        )
        
        # Add events
        cursor.execute("SELECT id FROM packages WHERE tracking_number = ?", (tracking_number,))
        row = cursor.fetchone()
        
        if row:
            for event in events:
                cursor.execute(
                    "INSERT INTO events (package_id, timestamp, location, description) VALUES (?, ?, ?, ?)",
                    (row["id"], event.get("time"), event.get("location"), event.get("description"))
                )
        
        conn.commit()
        conn.close()
        
        return {"success": True, "tracking_number": tracking_number}


def create_webhook_server(port: int = 8080):
    """Create Flask webhook server"""
    if not FLASK_AVAILABLE:
        print("Error: Flask is required for webhook server. Install with: pip install flask")
        sys.exit(1)
    
    app = Flask(__name__)
    tracker = Track17()
    
    @app.route("/webhook", methods=["POST"])
    def webhook():
        data = request.json
        result = tracker.handle_webhook(data)
        return jsonify(result)
    
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})
    
    return app


def main():
    parser = argparse.ArgumentParser(description="17TRACK Package Tracking")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Add package
    add_parser = subparsers.add_parser("add", help="Add package")
    add_parser.add_argument("--number", "-n", required=True, help="Tracking number")
    add_parser.add_argument("--carrier", "-c", help="Carrier code")
    
    # List packages
    list_parser = subparsers.add_parser("list", help="List packages")
    list_parser.add_argument("--status", "-s", default="all", 
                             help="Filter by status")
    
    # Get package
    get_parser = subparsers.add_parser("get", help="Get package details")
    get_parser.add_argument("--number", "-n", required=True, help="Tracking number")
    
    # Delete package
    del_parser = subparsers.add_parser("delete", help="Delete package")
    del_parser.add_argument("--number", "-n", required=True, help="Tracking number")
    
    # Sync
    sync_parser = subparsers.add_parser("sync", help="Sync packages")
    sync_parser.add_argument("--number", "-n", help="Specific package (optional)")
    
    # Import
    import_parser = subparsers.add_parser("import", help="Import packages")
    import_parser.add_argument("--file", "-f", required=True, help="CSV or JSON file")
    
    # Export
    export_parser = subparsers.add_parser("export", help="Export packages")
    export_parser.add_argument("--output", "-o", help="Output file")
    
    # Webhook
    webhook_parser = subparsers.add_parser("webhook", help="Start webhook server")
    webhook_parser.add_argument("--port", "-p", type=int, default=8080, help="Port")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize
    tracker = Track17()
    
    # Execute
    if args.command == "add":
        result = tracker.add(tracking_number=args.number, carrier=args.carrier)
    
    elif args.command == "list":
        result = tracker.list(status=args.status)
    
    elif args.command == "get":
        result = tracker.get(tracking_number=args.number)
    
    elif args.command == "delete":
        result = tracker.delete(tracking_number=args.number)
    
    elif args.command == "sync":
        result = tracker.sync(tracking_number=args.number)
    
    elif args.command == "import":
        result = tracker.import_packages(file_path=args.file)
    
    elif args.command == "export":
        result = tracker.export_packages(output_file=args.output)
    
    elif args.command == "webhook":
        print(f"Starting webhook server on port {args.port}...")
        app = create_webhook_server(port=args.port)
        app.run(host="0.0.0.0", port=args.port)
        return
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
