# 🔗 BlockTrack – Blockchain-Powered Order Tracking System

This project implements a fullstack solution for a **Blockchain-Based Order Tracking System**, developed as part of **Group 30** in the *Intelligent and Smart Supply Chain Management System* project.

It includes:

* **Hyperledger Fabric** (blockchain ledger)
* **IPFS** (for decentralized file storage)
* **Django REST Framework** (backend API)
<!-- * **Angular** (frontend for order interaction) -->

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
│   └── setup_the_chaincode.sh
│   └── invoke_the_chaincode.sh
│   └── invoke_addDocs.sh
│   └── invoke_updateDocs.sh
│   └── invoke_deleteDocs.sh
│   └── invoke_updateOrderStatus.sh
└── README.md
```

  

## ⚙️ Prerequisites

Before running this project, ensure you have:

* ✅ Python 3.10+ (for the backend)
* ✅ Go (for chaincode packaging)

  Install it by following the instructions at [go.dev/doc/install](https://go.dev/doc/install)
* ✅ jq (for parsing blockchain related configs)

  ```bash
  # On Ubuntu/Debian
  sudo apt-get install jq

  # On macOS
  brew install jq
  ```

> ⚠️ **Important:** All blockchain-related commands must be executed on a Linux/MacOS terminal. If you're on Windows, please use WSL (Windows Subsystem for Linux) to run these commands (Do not use terminals such as git bash).


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
<!-- 
> ✅ Note: Adjust `-ccp` if needed to point to your `chaincode-order` directory.
>

## ⚙️ One-Click Network Setup (Full Automation) -->

To make setup easier, we've included a shell script: `scripts/setup_the_chaincode.sh`

### 🔧 What It Does:
- Brings down any existing Fabric network
- Starts the test network with 2 organizations (Org1 + Org2)
- Packages the chaincode
- Installs it on both peers
- Approves chaincode definition for both orgs
- Commits chaincode
- Starts the IPFS container
- Ready for backend integration!

---

### 🚀 To Run It:
```bash
chmod +x scripts/setup_the_chaincode.sh
./scripts/setup_chaincode.sh
# 🔁 Make sure you're inside the test-network directory before running the script, and that you have installed both golang and jq.
```

You can test out the blockchain with the commands mentioned under [Sample Scripts](#sample-scripts)

---

### 3. Run the Django Backend
```bash
cd blocktrack_backend
python3 -m venv env
```
```bash
# if linux/ MAC
source ./env/bin/activate
# if windows
./env/scripts/activate
```
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

### 4. Shell Script Automation (Optional)
You can use a script for invoking blockchain:
```bash
chmod +x scripts/invoke_the_chaincode.sh
```
The Django view will run this script with proper environment to interact with peer CLI.

---

<!-- ### 5. Run the Angular Frontend (Deprecated)
```bash
cd blocktrack_frontend
npm install
ng serve
```
Open your browser at: [http://localhost:4200](http://localhost:4200)

--- -->

### 5. Start the Database with Docker Compose (Optional)
To start the database, use the provided `docker-compose.yaml` file:
```bash
cd blocktrack_backend
sudo docker-compose up -d
```
This will start the PostgreSQL database required for the backend.

---

### 6. Environment Variables
Ensure the following environment variables are set in a `.env` file within the `blocktrack_backend` folder

```env
SECRET_KEY=
DEBUG=False

DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

WAREHOUSE_SERVICE_URL=
USER_SERVICE_URL=
```

### 7. Dummy Data
Run the dummy.py as follows:
```bash
# On Linux/MacOS
python manage.py dummy_orders

# On Windows
python manage.py dummy_supplier_requests
```

### 8. View the API Documentation
Access the API documentation using Swagger UI by visiting:
```
http://127.0.0.1:8000/swagger
```
This provides an interactive interface to explore and test all available API endpoints.

---

## 🔌 API Endpoints

Run the django app and visit `/swagger` to view the swagger-UI docs

---
<!-- 
## 🖼️ Angular UI Pages

| Route                  | Function           |
|------------------------|--------------------|
| `/create-order`        | Upload + register  |
| `/read-order`          | Search order ID    |

--- -->

<!-- ## 🧪 Testing with Postman

Import the `config.postman.json` in `./blocktrack_backend` and checkout the endpoints -->

<!-- ### POST `/api/create-order/`
**Body:** `form-data`

| Key       | Type | Value                  |
|-----------|------|------------------------|
| order_id  | Text | `order901`             |
| status    | Text | `Packed`               |
| timestamp | Text | `2025-05-02T22:00:00Z` |
| document  | File | upload any file        |

### GET `/api/read-order/order901/`
- Returns the blockchain order details in JSON. -->

## Chaincode Logic (Go)

Chaincode functions:

- CreateOrder(ctx, id, status, timestamp, orderType, docHashesJSON)

- AddDocumentsToOrder(ctx, id, docHashesJSON)

- DeleteDocumentsFromOrder(ctx, id, docHashesJSON)

- UpdateOrderStatus(ctx, id, newStatus, newTimestamp)

- ReadOrder(ctx, id)

Each order is stored like:
```json
{
  "ID": "order901",
  "Status": "Packed",
  "Timestamp": "2025-05-02T22:00:00Z",
  "Type" : "ORD",
  "DocumentHashes": ["Qm...", "Qm...", ...]
}
```

### Sample Scripts

There are scripts to invoke each of the chaincode functions as bellow

```bash
# Call each of these scripts from the test-network directory

# Create Order
./scripts/invoke_the_chaincode.sh '{"Args":["46","Pending","2025-05-11T12:00:00Z","ORD", "[\"qweqwe\"]"]}'

# Update Order Status
./scripts/invoke_updateOrderStatus.sh '{"Args":["ORDER123","Shipped","2025-05-11T12:00:00Z"]}'

# Add doc hashes to Order
./scripts/invoke_addDocs.sh '{"Args":["46","[\"Qoija43wqtsduhawefiuh3124h2378urfei\"]"]}'

# Remove doc hashes from order
./scripts/invoke_deleteDocs.sh '{"Args":["46","[\"Hello2\"]"]}'
```

---

## 📂 IPFS Integration
- Files uploaded in Create Order go to IPFS.
- CID is stored on blockchain.
- You can access documents at:
```bash
http://localhost:8989/ipfs/<CID>
```

---

## 👨‍💼 Project Notes

- Developed by **Group 30** – Blockchain-Based Order Tracking
- Part of **Group H: Intelligent and Smart Supply Chain Management System**
- Frontend + Backend + Chaincode fully working

---
