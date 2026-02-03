#!/usr/bin/env python3
"""
IMAP/SMTP Email Skill - Read and send email via IMAP/SMTP
"""

import json
import sys
import argparse
import os
import email
import smtplib
import imaplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from typing import Dict, List, Optional
from datetime import datetime
import re


class EmailClient:
    """IMAP/SMTP Email client"""
    
    def __init__(self, imap_host: str, imap_port: int, imap_user: str, imap_password: str,
                 smtp_host: str, smtp_port: int, smtp_user: str, smtp_password: str):
        self.imap_host = imap_host
        self.imap_port = imap_port
        self.imap_user = imap_user
        self.imap_password = imap_password
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        
        self.imap_conn = None
        self.smtp_conn = None
    
    # IMAP Methods
    def imap_connect(self):
        """Connect to IMAP server"""
        try:
            self.imap_conn = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            self.imap_conn.login(self.imap_user, self.imap_password)
            return {"success": True, "message": "Connected to IMAP"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def imap_disconnect(self):
        """Disconnect from IMAP"""
        if self.imap_conn:
            self.imap_conn.logout()
            self.imap_conn = None
    
    def imap_folders(self) -> Dict:
        """List all folders"""
        if not self.imap_conn:
            result = self.imap_connect()
            if not result["success"]:
                return result
        
        try:
            status, folders = self.imap_conn.list()
            if status == "OK":
                folder_list = []
                for folder in folders:
                    name = folder.decode().split('"."')[-1].strip('"')
                    folder_list.append(name)
                return {"success": True, "folders": folder_list}
            else:
                return {"success": False, "error": "Failed to list folders"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            self.imap_disconnect()
    
    def imap_list(self, folder: str = "INBOX", limit: int = 20) -> Dict:
        """List messages in folder"""
        if not self.imap_conn:
            result = self.imap_connect()
            if not result["success"]:
                return result
        
        try:
            # Select folder
            status, data = self.imap_conn.select(folder)
            if status != "OK":
                return {"success": False, "error": f"Failed to select folder: {folder}"}
            
            # Search all messages
            status, messages = self.imap_conn.search(None, "ALL")
            if status != "OK":
                return {"success": False, "error": "Failed to search messages"}
            
            message_ids = messages[0].split()
            total = len(message_ids)
            
            # Get recent messages
            recent_ids = message_ids[-limit:] if limit else message_ids
            
            messages_list = []
            for msg_id in recent_ids:
                msg_data = self._fetch_message(msg_id)
                if msg_data:
                    messages_list.append(msg_data)
            
            return {
                "success": True,
                "folder": folder,
                "total": total,
                "count": len(messages_list),
                "messages": messages_list
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            self.imap_disconnect()
    
    def imap_search(self, query: str, folder: str = "INBOX") -> Dict:
        """Search messages"""
        if not self.imap_conn:
            result = self.imap_connect()
            if not result["success"]:
                return result
        
        try:
            status, data = self.imap_conn.select(folder)
            if status != "OK":
                return {"success": False, "error": f"Failed to select folder: {folder}"}
            
            status, messages = self.imap_conn.search(None, query)
            if status != "OK":
                return {"success": False, "error": "Search failed"}
            
            message_ids = messages[0].split()
            messages_list = []
            
            for msg_id in message_ids:
                msg_data = self._fetch_message(msg_id)
                if msg_data:
                    messages_list.append(msg_data)
            
            return {
                "success": True,
                "query": query,
                "folder": folder,
                "count": len(messages_list),
                "messages": messages_list
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            self.imap_disconnect()
    
    def imap_get(self, msg_id: str, include_body: bool = False) -> Dict:
        """Get single message"""
        if not self.imap_conn:
            result = self.imap_connect()
            if not result["success"]:
                return result
        
        try:
            msg_data = self._fetch_message(msg_id, include_body)
            if msg_data:
                return {"success": True, "message": msg_data}
            else:
                return {"success": False, "error": "Message not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            self.imap_disconnect()
    
    def imap_mark(self, msg_id: str, read: bool = True) -> Dict:
        """Mark message as read/unread"""
        if not self.imap_conn:
            result = self.imap_connect()
            if not result["success"]:
                return result
        
        try:
            flag = "\\Seen" if read else "\\Unseen"
            self.imap_conn.store(msg_id, "+FLAGS", flag)
            return {
                "success": True,
                "message": f"Marked as {'read' if read else 'unread'}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            self.imap_disconnect()
    
    def imap_download(self, msg_id: str, output_dir: str = "./downloads") -> Dict:
        """Download attachments from message"""
        if not self.imap_conn:
            result = self.imap_connect()
            if not result["success"]:
                return result
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            status, msg_data = self.imap_conn.fetch(msg_id, "(RFC822)")
            if status != "OK":
                return {"success": False, "error": "Failed to fetch message"}
            
            email_msg = email.message_from_bytes(msg_data[0][1])
            
            attachments = []
            for part in email_msg.walk():
                if part.get_content_disposition() == "attachment":
                    filename = part.get_filename()
                    if filename:
                        filepath = os.path.join(output_dir, filename)
                        with open(filepath, "wb") as f:
                            f.write(part.get_payload(decode=True))
                        attachments.append(filename)
            
            return {
                "success": True,
                "message_id": msg_id,
                "output_dir": output_dir,
                "attachments": attachments,
                "count": len(attachments)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            self.imap_disconnect()
    
    def _fetch_message(self, msg_id: str, include_body: bool = False) -> Optional[Dict]:
        """Fetch and parse message"""
        try:
            status, msg_data = self.imap_conn.fetch(msg_id, "(RFC822)")
            if status != "OK":
                return None
            
            email_msg = email.message_from_bytes(msg_data[0][1])
            
            # Extract headers
            subject = self._decode_header(email_msg.get("Subject", ""))
            from_addr = self._decode_header(email_msg.get("From", ""))
            to_addr = self._decode_header(email_msg.get("To", ""))
            date = email_msg.get("Date", "")
            
            # Extract body if requested
            body = ""
            if include_body:
                body = self._extract_body(email_msg)
            
            # Check for attachments
            has_attachments = any(
                part.get_content_disposition() == "attachment" 
                for part in email_msg.walk()
            )
            
            return {
                "id": msg_id.decode() if isinstance(msg_id, bytes) else str(msg_id),
                "subject": subject,
                "from": from_addr,
                "to": to_addr,
                "date": date,
                "has_attachments": has_attachments,
                "body": body[:2000] if body else "",
                "size": len(msg_data[0][1])
            }
        except Exception as e:
            print(f"Error fetching message: {e}")
            return None
    
    def _decode_header(self, header: str) -> str:
        """Decode email header"""
        if not header:
            return ""
        try:
            decoded = email.header.decode_header(header)
            return " ".join([
                part.decode(encoding or "utf-8", errors="replace") 
                if isinstance(part, bytes) else part 
                for part, encoding in decoded
            ])
        except Exception:
            return header
    
    def _extract_body(self, email_msg) -> str:
        """Extract message body"""
        body = ""
        for part in email_msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode(
                    part.get_content_charset() or "utf-8", errors="replace"
                )
                break
            elif part.get_content_type() == "text/html":
                body = part.get_payload(decode=True).decode(
                    part.get_content_charset() or "utf-8", errors="replace"
                )
        return body
    
    # SMTP Methods
    def smtp_connect(self):
        """Connect to SMTP server"""
        try:
            self.smtp_conn = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            self.smtp_conn.login(self.smtp_user, self.smtp_password)
            return {"success": True, "message": "Connected to SMTP"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def smtp_disconnect(self):
        """Disconnect from SMTP"""
        if self.smtp_conn:
            self.smtp_conn.quit()
            self.smtp_conn = None
    
    def smtp_send(self, to: str, subject: str, body: str = "",
                  html_body: str = None, attachments: List[str] = None) -> Dict:
        """Send email"""
        if not self.smtp_conn:
            result = self.smtp_connect()
            if not result["success"]:
                return result
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.smtp_user
            msg["To"] = to
            msg["Subject"] = subject
            
            # Add body
            if html_body:
                msg.attach(MIMEText(html_body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))
            
            # Add attachments
            if attachments:
                for filepath in attachments:
                    if os.path.exists(filepath):
                        part = MIMEBase("application", "octet-stream")
                        with open(filepath, "rb") as f:
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename= {os.path.basename(filepath)}"
                        )
                        msg.attach(part)
            
            # Send
            self.smtp_conn.send_message(msg)
            
            return {
                "success": True,
                "to": to,
                "subject": subject,
                "message": "Email sent successfully"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            self.smtp_disconnect()


def main():
    parser = argparse.ArgumentParser(description="IMAP/SMTP Email Skill")
    subparsers = parser.add_subparsers(dest="protocol", help="Protocol")
    
    # IMAP subparser
    imap_parser = subparsers.add_parser("imap", help="IMAP commands")
    imap_subparsers = imap_parser.add_subparsers(dest="command", help="IMAP commands")
    
    imap_subparsers.add_parser("folders", help="List folders")
    
    list_parser = imap_subparsers.add_parser("list", help="List messages")
    list_parser.add_argument("--folder", default="INBOX", help="Folder name")
    list_parser.add_argument("--limit", type=int, default=20, help="Max messages")
    
    search_parser = imap_subparsers.add_parser("search", help="Search messages")
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.add_argument("--folder", default="INBOX", help="Folder name")
    
    get_parser = imap_subparsers.add_parser("get", help="Get message")
    get_parser.add_argument("--id", required=True, help="Message ID")
    get_parser.add_argument("--include-body", action="store_true", help="Include body")
    
    mark_parser = imap_subparsers.add_parser("mark", help="Mark message")
    mark_parser.add_argument("--id", required=True, help="Message ID")
    mark_group = mark_parser.add_mutually_exclusive_group(required=True)
    mark_group.add_argument("--read", action="store_true", help="Mark as read")
    mark_group.add_argument("--unread", action="store_true", help="Mark as unread")
    
    download_parser = imap_subparsers.add_parser("download", help="Download attachments")
    download_parser.add_argument("--id", required=True, help="Message ID")
    download_parser.add_argument("--output", default="./downloads", help="Output directory")
    
    # SMTP subparser
    smtp_parser = subparsers.add_parser("smtp", help="SMTP commands")
    smtp_subparsers = smtp_parser.add_subparsers(dest="command", help="SMTP commands")
    
    send_parser = smtp_subparsers.add_parser("send", help="Send email")
    send_parser.add_argument("--to", required=True, help="Recipient email")
    send_parser.add_argument("--subject", "-s", required=True, help="Subject")
    send_parser.add_argument("--body", "-b", help="Plain text body")
    send_parser.add_argument("--html", help="HTML body")
    send_parser.add_argument("--attachment", "-a", action="append", help="Attachment paths")
    
    args = parser.parse_args()
    
    # Get credentials from environment
    imap_host = os.environ.get("IMAP_HOST", "imap.gmail.com")
    imap_port = int(os.environ.get("IMAP_PORT", 993))
    imap_user = os.environ.get("IMAP_USER")
    imap_password = os.environ.get("IMAP_PASSWORD")
    
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 465))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    
    if not imap_user or not imap_password:
        print(json.dumps({"success": False, "error": "Missing IMAP credentials"}, ensure_ascii=False))
        sys.exit(1)
    
    client = EmailClient(
        imap_host=imap_host, imap_port=imap_port, imap_user=imap_user, imap_password=imap_password,
        smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password
    )
    
    # Execute
    if args.protocol == "imap":
        if args.command == "folders":
            result = client.imap_folders()
        elif args.command == "list":
            result = client.imap_list(folder=args.folder, limit=args.limit)
        elif args.command == "search":
            result = client.imap_search(query=args.query, folder=args.folder)
        elif args.command == "get":
            result = client.imap_get(msg_id=args.id, include_body=args.include_body)
        elif args.command == "mark":
            result = client.imap_mark(msg_id=args.id, read=args.read)
        elif args.command == "download":
            result = client.imap_download(msg_id=args.id, output_dir=args.output)
        else:
            imap_parser.print_help()
            sys.exit(1)
    
    elif args.protocol == "smtp":
        if args.command == "send":
            if not smtp_user or not smtp_password:
                print(json.dumps({"success": False, "error": "Missing SMTP credentials"}, ensure_ascii=False))
                sys.exit(1)
            result = client.smtp_send(
                to=args.to,
                subject=args.subject,
                body=args.body or "",
                html_body=args.html,
                attachments=args.attachment
            )
        else:
            smtp_parser.print_help()
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
