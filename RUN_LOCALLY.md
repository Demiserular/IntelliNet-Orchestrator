# 🚀 Run IntelliNet Orchestrator Locally (No Docker Compose)

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ installed  
- Neo4j running (can use Docker for just Neo4j)

---

## Step 1: Start Neo4j

**In your terminal, run:**

```powershell
docker run -d --name neo4j-local `
  -p 7474:7474 -p 7687:7687 `
  -e NEO4J_AUTH=neo4j/devpassword123 `
  neo4j:5.12
```

**Verify it's running:**
```powershell
docker ps | findstr neo4j
```

**Access Neo4j Browser:** http://localhost:7474
- Username: `neo4j`
- Password: `devpassword123`

---

## Step 2: Start the Backend (Python/FastAPI)

**Open a NEW terminal window** and run:

```powershell
# Make sure you're in the project root directory
cd "C:\Users\sc895\Project\OG projects"

# Run the backend
python main.py
```

**You should see:**
```
Starting IntelliNet Orchestrator
API Host: 0.0.0.0
API Port: 8000
...
```

**Verify backend is running:**
- API Docs: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/health

**Keep this terminal open!**

---

## Step 3: Serve the Frontend (Angular)

The frontend is already built in `frontend/dist/intellinet-orchestrator/`.

**Option A: Using Python's HTTP Server (Simplest)**

**Open ANOTHER NEW terminal window** and run:

```powershell
# Navigate to the built frontend
cd "C:\Users\sc895\Project\OG projects\frontend\dist\intellinet-orchestrator"

# Serve it on port 4200
python -m http.server 4200
```

**Access the app:** http://localhost:4200

---

**Option B: Using Angular Dev Server (If you want hot reload)**

**Open ANOTHER NEW terminal window** and run:

```powershell
# Navigate to frontend directory
cd "C:\Users\sc895\Project\OG projects\frontend"

# Start Angular dev server
npm start
```

**Access the app:** http://localhost:4200

**Keep this terminal open!**

---

## Step 4: Initialize the Database

**Open ANOTHER NEW terminal window** and run:

```powershell
cd "C:\Users\sc895\Project\OG projects"

# Initialize database with admin user
python scripts/init_db.py

# Populate sample data (optional but recommended)
python scripts/populate_sample_data.py
```

---

## Step 5: Access the Application

**Open your browser:**

- **Frontend**: http://localhost:4200
- **API Docs**: http://localhost:8000/api/docs
- **Neo4j Browser**: http://localhost:7474

**Login credentials:**
- Username: `admin`
- Password: `admin123`

---

## 🎯 Quick Commands Summary

**Terminal 1 - Neo4j:**
```powershell
docker run -d --name neo4j-local -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/devpassword123 neo4j:5.12
```

**Terminal 2 - Backend:**
```powershell
python main.py
```

**Terminal 3 - Frontend:**
```powershell
cd frontend\dist\intellinet-orchestrator
python -m http.server 4200
```

**Terminal 4 - Initialize (one-time):**
```powershell
python scripts/init_db.py
python scripts/populate_sample_data.py
```

---

## 🛑 Stopping Everything

**Stop Backend:** Press `Ctrl+C` in Terminal 2

**Stop Frontend:** Press `Ctrl+C` in Terminal 3

**Stop Neo4j:**
```powershell
docker stop neo4j-local
docker rm neo4j-local
```

---

## 🐛 Troubleshooting

### Backend won't start
- **Error: "Neo4j connection failed"**
  - Make sure Neo4j is running: `docker ps | findstr neo4j`
  - Check credentials in `.env` file match: `neo4j/devpassword123`

### Frontend shows blank page
- Check browser console for errors (F12)
- Make sure backend is running on port 8000
- Try accessing API directly: http://localhost:8000/health

### Port already in use
- **Port 8000**: Another app is using it. Stop it or change port in `.env`
- **Port 4200**: Stop other Angular apps or use different port: `python -m http.server 4201`
- **Port 7687/7474**: Stop other Neo4j instances: `docker ps`

### CORS errors in browser
- Make sure backend is running
- Check `.env` has: `API_CORS_ORIGINS=http://localhost:4200`

---

## ✅ You're All Set!

Now you can:
1. **Login** at http://localhost:4200
2. **View topology** - See the sample network
3. **Provision services** - Create new services
4. **Check analytics** - View metrics
5. **Explore API** - http://localhost:8000/api/docs

Enjoy! 🎉
