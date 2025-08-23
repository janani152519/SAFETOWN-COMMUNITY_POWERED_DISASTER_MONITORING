from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector

app = FastAPI()

# Allow Frontend Access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class Alert(BaseModel):
    host_name: str
    type: str
    title: str
    severity: str
    tips: str
    status: str
    lat: float
    lng: float

class User(BaseModel):
    name: str

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="safetown"
    )

# Routes
@app.get("/alerts/")
def get_alerts():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM alerts ORDER BY created_at DESC")
    results = cursor.fetchall()
    cursor.close()
    db.close()
    return results

@app.post("/alerts/")
def add_alert(alert: Alert):
    db = get_db()
    cursor = db.cursor()
    sql = """INSERT INTO alerts (host_name, type, title, severity, status, tips, lat, lng)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
    values = (alert.host_name, alert.type, alert.title, alert.severity, alert.status, alert.tips, alert.lat, alert.lng)
    cursor.execute(sql, values)
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Alert added successfully!"}

@app.get("/leaderboard/")
def leaderboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT name, points FROM users ORDER BY points DESC LIMIT 10")
    results = cursor.fetchall()
    cursor.close()
    db.close()
    return results

@app.post("/login/")
def login(user: User):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE name = %s", (user.name,))
    existing = cursor.fetchone()
    if existing:
        cursor.close()
        db.close()
        return {"message": "Login successful", "name": user.name}
    else:
        cursor.execute("INSERT INTO users (name, points) VALUES (%s,%s)", (user.name, 0))
        db.commit()
        cursor.close()
        db.close()
        return {"message": "User created", "name": user.name}

@app.post("/points/")
def add_points(user: User):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE users SET points = points + 1 WHERE name = %s", (user.name,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Points updated"}