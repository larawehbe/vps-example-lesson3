# 📝 TodoApp — FastAPI + PostgreSQL on a VPS

A minimal but production-structured REST API built with **FastAPI** and **PostgreSQL**, designed to run on a Linux VPS (Ubuntu 22.04). This project is part of a demo contrasting self-managed database hosting on a VPS versus managed services like AWS RDS.

---

## 📁 Project Structure

```
todoapp/
├── main.py           # FastAPI app + route definitions
├── database.py       # SQLAlchemy engine, session, and base
├── models.py         # ORM table definitions
├── schemas.py        # Pydantic request/response schemas
├── requirements.txt  # Python dependencies
└── .env              # Environment variables (not committed to git)
```

---

## ⚙️ Requirements

- Ubuntu 22.04 LTS (or any Debian-based Linux)
- Python 3.10+
- PostgreSQL 14+
- A VPS with root or sudo access (e.g. Hostinger VPS)

---

## 🚀 Setup Guide

### 1. System Dependencies

```bash
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv postgresql postgresql-contrib -y
```

---

### 2. PostgreSQL Setup

Switch to the postgres system user and open the psql shell:

```bash
su - postgres
psql
```

Run the following SQL commands:

```sql
CREATE DATABASE tododb;
CREATE USER todouser WITH ENCRYPTED PASSWORD 'todopass';
GRANT ALL PRIVILEGES ON DATABASE tododb TO todouser;
\q
```

> **PostgreSQL 15+ note:** Version 15 revoked the default `CREATE` privilege on the `public` schema. If you're on PostgreSQL 15 or newer, run this additional step:

```bash
psql -d tododb
```

```sql
GRANT USAGE ON SCHEMA public TO todouser;
GRANT CREATE ON SCHEMA public TO todouser;
\q
```

Exit back to root:

```bash
exit
```

---

### 3. Clone & Configure the Project

```bash
mkdir todoapp && cd todoapp
python3 -m venv venv
source venv/bin/activate
```

Create a `.env` file:

```bash
nano .env
```

Add the following:

```env
DATABASE_URL=postgresql://todouser:todopass@localhost:5432/tododb
```

---

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

**`requirements.txt`**
```
fastapi
uvicorn
sqlalchemy
psycopg2-binary
python-dotenv
```

---

### 5. Run the App

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The app will be available at:

```
http://YOUR_VPS_IP:8000
```

Interactive API docs (Swagger UI):

```
http://YOUR_VPS_IP:8000/docs
```

---

### 6. Open the Firewall Port

```bash
ufw allow OpenSSH
ufw allow 8000/tcp
ufw enable
ufw status
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/todos` | List all todos |
| `POST` | `/todos` | Create a new todo |
| `PATCH` | `/todos/{id}` | Mark a todo as done/undone |
| `DELETE` | `/todos/{id}` | Delete a todo |

---

### Example Requests

**Create a todo:**
```bash
curl -X POST http://YOUR_VPS_IP:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries"}'
```

**Get all todos:**
```bash
curl http://YOUR_VPS_IP:8000/todos
```

**Mark as done:**
```bash
curl -X PATCH http://YOUR_VPS_IP:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'
```

**Delete a todo:**
```bash
curl -X DELETE http://YOUR_VPS_IP:8000/todos/1
```

---

## 🗄️ Database Schema

```sql
CREATE TABLE todos (
    id    SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    done  BOOLEAN DEFAULT FALSE
);
```

The table is created automatically on app startup via SQLAlchemy's `create_all()`.

---

## 🔁 Run as a systemd Service (Optional)

To keep the app running after reboots, create a systemd unit file:

```bash
nano /etc/systemd/system/todoapp.service
```

```ini
[Unit]
Description=TodoApp FastAPI Service
After=network.target

[Service]
User=root
WorkingDirectory=/root/todoapp
Environment="PATH=/root/todoapp/venv/bin"
ExecStart=/root/todoapp/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
systemctl daemon-reload
systemctl enable todoapp
systemctl start todoapp
systemctl status todoapp
```

---

## 🔄 Manual Backup (the VPS reality)

Unlike AWS RDS, there are no automatic backups. You do it yourself:

```bash
pg_dump -U todouser -h localhost tododb > backup_$(date +%Y%m%d).sql
```

Restore from backup:

```bash
psql -U todouser -h localhost tododb < backup_20240101.sql
```

Automate it with a cron job:

```bash
crontab -e
```

```
0 2 * * * pg_dump -U todouser -h localhost tododb > /root/backups/backup_$(date +\%Y\%m\%d).sql
```

---

## 🐞 Common Issues

| Error | Cause | Fix |
|-------|-------|-----|
| `permission denied for schema public` | PostgreSQL 15+ changed default schema permissions | Grant `USAGE` and `CREATE` on schema `public` to your user |
| `connection refused` on port 5432 | PostgreSQL only listening on localhost | Set `listen_addresses = '*'` in `postgresql.conf` |
| `port 8000 unreachable` | UFW blocking the port | Run `ufw allow 8000/tcp` |
| `could not connect to server` | Wrong credentials in `.env` | Double-check `DATABASE_URL` values |

---

## 📌 VPS vs Managed RDS — What This Demo Highlights

| Task | This VPS Setup | AWS RDS |
|------|---------------|---------|
| Database installation | Manual (`apt install`) | Pre-installed |
| User & permission setup | Manual SQL commands | Wizard during creation |
| Schema permissions (PG15) | Manual grant required | Handled automatically |
| Remote access config | Edit `pg_hba.conf` + firewall | Toggle in AWS console |
| Backups | Manual `pg_dump` or cron | Automatic, point-in-time |
| Failover | Not configured | Multi-AZ toggle |
| Monitoring | Not configured | CloudWatch built-in |
| OS patching | `apt upgrade` — your job | Fully managed |

---

## 📄 License

MIT — free to use for demos, tutorials, and learning projects.
