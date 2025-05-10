# 🔗 BlockTrack – Blockchain-Powered Order Tracking System

This project implements a fullstack solution for a **Blockchain-Based Order Tracking System**, developed as part of **Group 30** in the *Intelligent and Smart Supply Chain Management System* project.

It includes:

* **Hyperledger Fabric** (blockchain ledger)
* **IPFS** (for decentralized file storage)
* **Django REST Framework** (backend API)
* **Angular** (frontend for order interaction)

---

## 📦 Folder Structure

```
blocktrack/
├── blocktrack_backend/        # Django API project
│   ├── api/                   # Views and IPFS utils
│   ├── manage.py
│   └── requirements.txt
├── blocktrack_frontend/       # Angular frontend app
│   ├── src/app/create-order/  # Order creation UI
│   ├── src/app/read-order/    # Read order UI
│   └── angular.json
├── chaincode-order/           # Go chaincode
│   └── order.go
├── scripts/                   # Shell automation scripts
│   └── invoke_order.sh
└── README.md
```

---

## ⚙️ Prerequisites

Before running this project, ensure you have:

* ✅ [Docker](https://www.docker.com/)
* ✅ [Hyperledger Fabric Samples](https://hyperledger-fabric.readthedocs.io/en/latest/test_network.html)
* ✅ [IPFS Desktop](https://docs.ipfs.tech/install/ipfs-desktop/) or run `ipfs daemon`
* ✅ Python 3.10+
* ✅ Go (for chaincode)
* ✅ Node.js + Angular CLI (for frontend)

---

## 🚀 How to Run the Project

### 1. Clone the Repo
```bash
git clone https://github.com/IASSCMS/Order-Tracking-BlockTrack.git
cd blocktrack
```

---

### 2. Start the Blockchain Network
From your Fabric samples directory:
```bash
curl -sSL https://bit.ly/2ysbOFE | bash -s -- -d -s
cd ./test-network

```

> ✅ Note: Adjust `-ccp` if needed to point to your `chaincode-order` directory.
>
> ## ⚙️ One-Click Network Setup (Full Automation)

To make setup easier, we’ve included a shell script: `scripts/setup_chaincode.sh`

### 🔧 What It Does:
- Brings down any existing Fabric network
- Starts the test network with 2 organizations (Org1 + Org2)
- Packages the chaincode
- Installs it on both peers
- Approves chaincode definition for both orgs
- Commits chaincode
- Ready for backend integration!

---

### 🚀 To Run It:
```bash
chmod +x scripts/setup_chaincode.sh
./scripts/setup_chaincode.sh
🔁 Make sure you're inside the test-network directory before running the script.

---

### 3. Start IPFS
Run either:
```bash
# Option A
Open IPFS Desktop

# Option B
ipfs daemon
```

---

### 4. Run the Django Backend
```bash
cd blocktrack_backend
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

### 5. Shell Script Automation (Optional)
You can use a script for invoking blockchain:
```bash
chmod +x scripts/invoke_order.sh
```
The Django view will run this script with proper environment to interact with peer CLI.

---

### 6. Run the Angular Frontend
```bash
cd blocktrack_frontend
npm install
ng serve
```
Open your browser at: [http://localhost:4200](http://localhost:4200)

---

### 7. Start the Database with Docker Compose
To start the database, use the provided `docker-compose.yaml` file:
```bash
cd blocktrack_backend
sudo docker-compose up -d
```
This will start the PostgreSQL database required for the backend.

### 8. Environment Variables
Ensure the following environment variables are set for the backend:

```env
DATABASE_NAME=blocktrack_db
DATABASE_USER=blocktrack_user
DATABASE_PASSWORD=securepassword
DATABASE_HOST=localhost
DATABASE_PORT=5432
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=*
```

### 9. Dummy Data
Run the dummy.py as follows:
```bash
# On Linux/MacOS
python manage.py shell < dummy.py

# On Windows
python manage.py shell < dummy.py
```

---

## 🔌 API Endpoints

Run the django app and visit `/swagger` to view the swagger-UI docs

---

## 🖼️ Angular UI Pages

| Route                  | Function           |
|------------------------|--------------------|
| `/create-order`        | Upload + register  |
| `/read-order`          | Search order ID    |

---

## 🧪 Testing with Postman

### POST `/api/create-order/`
**Body:** `form-data`

| Key       | Type | Value                  |
|-----------|------|------------------------|
| order_id  | Text | `order901`             |
| status    | Text | `Packed`               |
| timestamp | Text | `2025-05-02T22:00:00Z` |
| document  | File | upload any file        |

### GET `/api/read-order/order901/`
- Returns the blockchain order details in JSON.

---

## 🔧 Chaincode Logic (Go)

Chaincode functions:
```go
CreateOrder(ctx, id, status, timestamp, docHash)
ReadOrder(ctx, id)
```

Each order is stored like:
```json
{
  "ID": "order901",
  "Status": "Packed",
  "Timestamp": "2025-05-02T22:00:00Z",
  "DocumentHash": "Qm..."
}
```

---

## 📂 IPFS Integration
- Files uploaded in Create Order go to IPFS.
- CID is stored on blockchain.
- You can access documents at:
```bash
https://ipfs.io/ipfs/<CID>
```

---

## 👨‍💼 Project Notes

- Developed by **Group 30** – Blockchain-Based Order Tracking
- Part of **Group H: Intelligent and Smart Supply Chain Management System**
- Frontend + Backend + Chaincode fully working

---




