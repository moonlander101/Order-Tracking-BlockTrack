# 🔗 BlockTrack – Blockchain-Powered Order Tracking System

This project implements a backend for a **Blockchain-Based Order Tracking System**, developed as part of **Group 30** in the *Intelligent and Smart Supply Chain Management System* project.

It uses:

* **Hyperledger Fabric** (blockchain network)
* **IPFS** (for decentralized file storage)
* **Django REST Framework** (backend API)

---

## 📦 Folder Structure

```
blocktrack/
├── blocktrack_backend/        # Django API project
│   ├── api/                   # Views and IPFS utils
│   ├── manage.py
│   └── requirements.txt
├── chaincode-order/           # Go chaincode
│   └── order.go
├── .gitignore
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
cd ~/hyperledger-fabric/fabric-samples/test-network
./network.sh down
./network.sh up createChannel -ca
./network.sh deployCC -ccn ordercc -ccp ../order-tracking/chaincode-order -ccl go
```

> Note: Adjust the chaincode path `-ccp` if necessary to point to `chaincode-order`.

---

### 3. Start IPFS

Run either:

* **IPFS Desktop**, or
* CLI: `ipfs daemon`

---

### 4. Run the Django Backend

```bash
cd blocktrack_backend
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

---

## 🔌 API Endpoints

| Method | URL                           | Description                    |
| ------ | ----------------------------- | ------------------------------ |
| POST   | `/api/create-order/`          | Create an order with file      |
| GET    | `/api/read-order/<order_id>/` | Retrieve order from blockchain |

---

### 🦪 Sample POST Request (in Postman)

**POST** `http://127.0.0.1:8000/api/create-order/`
**Body type:** `form-data`

| Key       | Type | Value                  |
| --------- | ---- | ---------------------- |
| order\_id | Text | `order901`             |
| status    | Text | `Packed`               |
| timestamp | Text | `2025-05-02T22:00:00Z` |
| document  | File | (upload a small file)  |

---

## 🔧 Chaincode Logic (Go)

Your chaincode handles:

```go
CreateOrder(ctx, id, status, timestamp, docHash)
ReadOrder(ctx, id)
```

Each order is stored on the ledger like this:

```json
{
  "ID": "order901",
  "Status": "Packed",
  "Timestamp": "2025-05-02T22:00:00Z",
  "DocumentHash": "Qm..."
}
```

---

## 📂 IPFS

Uploaded documents are stored in IPFS and linked via CID (`Qm...`).
To access them directly:

```text
https://ipfs.io/ipfs/<CID>
```

---

## 👨‍💼 Project Notes

* Developed by **Group 30** – Blockchain-Based Order Tracking
* Part of **Group H: Intelligent Supply Chain Management System**
* For internal testing & collaboration – frontend not included yet

---

## 📞 Questions?

Ping Pasindu or teammates via GitHub or your project group.

---
