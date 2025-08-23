# backend.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import mysql.connector
from fastapi import FastAPI


app = FastAPI(title="XAMPP MySQL Alert API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev
    allow_methods=["*"],
    allow_headers=["*"],
)

# MySQL connection function
def get_connection():
    return mysql.connector.connect(
        host="localhost",   # XAMPP default
        user="root",        # XAMPP default user
        password="",        # Leave empty if no password
        database="safetown_db",
        autocommit=True
    )

# Models
class Alert(BaseModel):
    host_name: str
    type: str
    title: str
    severity: str
    tips: str
    status: str
    lat: float
    lng: float

class AlertResponse(Alert):
    id: int

# Health Check
@app.get("/health")
def health():
    return {"status": "API is running"}

# Insert Alert
@app.post("/alerts/", response_model=AlertResponse)
def create_alert(alert: Alert):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO alerts (host_name, type, title, severity, tips, status, lat, lng)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (alert.host_name, alert.type, alert.title, alert.severity,
              alert.tips, alert.status, alert.lat, alert.lng))
        alert_id = cur.lastrowid
        return AlertResponse(id=alert_id, **alert.dict())
    finally:
        cur.close()
        conn.close()

# Get All Alerts
@app.get("/alerts/", response_model=List[AlertResponse])
def get_all_alerts():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, host_name, type, title, severity, tips, status, lat, lng FROM alerts ORDER BY id DESC")
        rows = cur.fetchall()
        return [AlertResponse(
            id=row[0], host_name=row[1], type=row[2], title=row[3],
            severity=row[4], tips=row[5], status=row[6], lat=row[7], lng=row[8]
        ) for row in rows]
    finally:
        cur.close()
        conn.close()

# Get Single Alert
@app.get("/alerts/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: int):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, host_name, type, title, severity, tips, status, lat, lng FROM alerts WHERE id=%s", (alert_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Alert not found")
        return AlertResponse(
            id=row[0], host_name=row[1], type=row[2], title=row[3],
            severity=row[4], tips=row[5], status=row[6], lat=row[7], lng=row[8]
        )
    finally:
        cur.close()
        conn.close()
