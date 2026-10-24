#!/usr/bin/env python3
"""Sully TV local DVR. Python stdlib + FFmpeg; no paid services."""
import argparse
import hmac
import json
import os
import secrets
import shutil
import subprocess
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "recordings"
DATA.mkdir(exist_ok=True)
JOBS = {}
LOCK = threading.Lock()
TOKEN = os.environ.get("SULLY_DVR_TOKEN", "")
MAX_SECONDS = 4 * 3600

def snapshot():
    with LOCK:
        for job in JOBS.values():
            proc = job.get("_process")
            if proc and job["status"] == "recording" and proc.poll() is not None:
                job["status"] = "completed" if proc.returncode == 0 and (DATA / (job["id"] + ".ts")).exists() else "failed"
                job["ended"] = datetime.now(timezone.utc).isoformat()
        return [{k:v for k,v in job.items() if not k.startswith("_")} for job in JOBS.values()]

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("%s %s" % (self.address_string(), fmt % args), flush=True)

    def auth(self):
        provided = self.headers.get("Authorization", "")
        if not TOKEN or not hmac.compare_digest(provided, "Bearer " + TOKEN):
            self.send_json(401, {"error":"Unauthorized"})
            return False
        return True

    def send_json(self, status, value):
        payload = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if not self.auth(): return
        if self.path == "/api/recordings":
            self.send_json(200, {"recordings": snapshot()})
            return
        if self.path.startswith("/api/recordings/") and self.path.endswith("/download"):
            ident = self.path.split("/")[3]
            if not valid_id(ident):
                return self.send_json(400, {"error":"Invalid ID"})
            path = DATA / (ident + ".ts")
            if not path.is_file():
                return self.send_json(404, {"error":"Not found"})
            self.send_response(200)
            self.send_header("Content-Type", "video/mp2t")
            self.send_header("Content-Disposition", 'attachment; filename="sully-'+ident+'.ts"')
            self.send_header("Content-Length", str(path.stat().st_size))
            self.end_headers()
            with path.open("rb") as f:
                shutil.copyfileobj(f, self.wfile)
            return
        self.send_json(404, {"error":"Not found"})

    def do_POST(self):
        if not self.auth(): return
        if self.path != "/api/recordings":
            return self.send_json(404, {"error":"Not found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 4096: raise ValueError("Invalid request size")
            data = json.loads(self.rfile.read(length))
            url = data["url"]
            title = str(data.get("title", "Sully TV recording"))[:120]
            duration = int(data.get("duration_seconds", 1800))
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password:
                raise ValueError("Direct HTTP(S) stream URL required")
            if not 1 <= duration <= MAX_SECONDS:
                raise ValueError("Duration must be between 1 second and 4 hours")
            if shutil.which("ffmpeg") is None:
                return self.send_json(503, {"error":"FFmpeg is not installed"})
            ident = uuid.uuid4().hex
            output = DATA / (ident + ".ts")
            cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
                   "-i", url, "-t", str(duration), "-map", "0:v:0?", "-map", "0:a:0?",
                   "-c", "copy", "-f", "mpegts", str(output)]
            with (DATA / (ident + ".log")).open("wb") as log:
                proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                        stderr=log, start_new_session=True)
            job = {"id":ident,"title":title,"status":"recording","duration_seconds":duration,
                   "started":datetime.now(timezone.utc).isoformat(),"_process":proc}
            with LOCK: JOBS[ident] = job
            self.send_json(201, {"id":ident,"status":"recording"})
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
            self.send_json(400, {"error":str(e)})
        except OSError:
            self.send_json(500, {"error":"Unable to start FFmpeg"})

    def do_DELETE(self):
        if not self.auth(): return
        parts = self.path.split("/")
        if len(parts) != 4 or parts[:3] != ["", "api", "recordings"] or not valid_id(parts[3]):
            return self.send_json(404, {"error":"Not found"})
        ident = parts[3]
        with LOCK:
            job = JOBS.get(ident)
            if job and job["status"] == "recording":
                return self.send_json(409, {"error":"Recording in progress; stop it first"})
            JOBS.pop(ident, None)
        removed = False
        for suffix in (".ts", ".log"):
            path = DATA / (ident + suffix)
            if path.exists():
                path.unlink()
                removed = True
        self.send_json(200 if removed else 404, {"deleted":removed})

def valid_id(value):
    return len(value) == 32 and all(c in "0123456789abcdef" for c in value)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if not TOKEN or len(TOKEN) < 24:
        raise SystemExit("Set SULLY_DVR_TOKEN to a random secret of at least 24 characters")
    if args.host not in ("127.0.0.1", "localhost", "::1"):
        raise SystemExit("Only loopback binding is supported; use a secure private tunnel for remote access")
    print("Sully DVR listening on http://%s:%d" % (args.host, args.port), flush=True)
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()

if __name__ == "__main__":
    main()
