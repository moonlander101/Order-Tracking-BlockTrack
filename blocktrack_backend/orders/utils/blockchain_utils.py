import json
import os
from pathlib import Path
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent  # → blocktrack_backend/
FABRIC_BASE = PROJECT_ROOT / "test-network" / ".."
FABRIC_BASE = FABRIC_BASE.resolve()

BIN_PATH = FABRIC_BASE / "bin"
CONFIG_PATH = FABRIC_BASE / "config"
TEST_NETWORK = FABRIC_BASE / "test-network"

CREATE_ORDER_SCRIPT_PATH = FABRIC_BASE / "test-network" / "scripts" / "invoke_the_chaincode.sh"
ADD_DOCS_SCRIPT_PATH = FABRIC_BASE / "test-network" / "scripts" / "invoke_addDocs.sh"
UPDATE_DOCS_SCRIPT_PATH = FABRIC_BASE / "test-network" / "scripts" / "invoke_updateOrderStatus.sh"

def get_fabric_env():
    env = os.environ.copy()
    env["PATH"] = f"{BIN_PATH}:" + env["PATH"]
    env["FABRIC_CFG_PATH"] = f"{FABRIC_BASE}/config"
    env["CORE_PEER_LOCALMSPID"] = "Org1MSP"
    env["CORE_PEER_TLS_ENABLED"] = "true"
    env["CORE_PEER_TLS_ROOTCERT_FILE"] = f"{TEST_NETWORK}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt"
    env["CORE_PEER_MSPCONFIGPATH"] = f"{TEST_NETWORK}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp"
    env["CORE_PEER_ADDRESS"] = "localhost:7051"
    return env

def invoke_create_order(order_id, timestamp, status, order_type, documentHashes=[]):
    fabric_env = get_fabric_env()
    
    if (order_type != "ORD" and order_type != "SR"):
        raise Exception("Invalid Order Status")

    args_json = json.dumps({
        "function": "CreateOrder",
        "Args": [order_id, status, timestamp, order_type, json.dumps(documentHashes)]
    })

    print("🔧 Executing:", CREATE_ORDER_SCRIPT_PATH, args_json)

    result = subprocess.run(
        [str(CREATE_ORDER_SCRIPT_PATH), args_json],
        capture_output=True,
        text=True,
        env=fabric_env
    )

    print("✅ STDOUT:", result.stdout)
    print("❌ STDERR:", result.stderr)

    if result.returncode != 0:
        raise Exception(f"Invoke script failed:\n{result.stderr}")

    # return Response({
    #     "message": "Order created",
    #     "cid": cid,
    #     "blockchain_response": result.stdout.strip()
    # })

def invoke_add_docs(order_id, docHashes):
    fabric_env = get_fabric_env()
    
    args_json = json.dumps({
        "function": "AddDocumentsToOrder",
        "Args": [order_id, json.dumps(docHashes)]
    })

    print("🔧 Executing:", ADD_DOCS_SCRIPT_PATH, args_json)

    result = subprocess.run(
        [str(ADD_DOCS_SCRIPT_PATH), args_json],
        capture_output=True,
        text=True,
        env=fabric_env
    )

    print("✅ STDOUT:", result.stdout)
    # print("❌ STDERR:", result.stderr)

    if result.returncode != 0:
        raise Exception(f"Invoke script failed:\n{result.stderr}")
    

def invoke_read_order(order_id):
    if not order_id:
        # return Response({"error": "Order ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        raise Exception({"error": "Order ID is required"})
    
    fabric_env = get_fabric_env()

    # Safely formatted single-line command
    command = [
        "peer", "chaincode", "query",
        "--tls",
        "--cafile", str(TEST_NETWORK / "organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem"),
        "--peerAddresses", "localhost:7051",
        "--tlsRootCertFiles", str(TEST_NETWORK / "organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt"),
        "-C", "mychannel",
        "-n", "ordercc",
        "-c", f'{{"Args":["ReadOrder", "{order_id}"]}}'
    ]

    print("🔍 Executing ReadOrder command for:", order_id)

    try:
        result = subprocess.run(command, capture_output=True, text=True, env=fabric_env)

        if result.returncode != 0:
            # return Response({
            #     "error": f"Failed to read order '{order_id}' from blockchain",
            #     "details": result.stderr.strip()
            # }, status=404)
            raise Exception({
                "error": f"Failed to read order '{order_id}' from blockchain",
                "details": result.stderr.strip()
            })

        return {
            "order_id": order_id,
            "blockchain_data": json.loads(result.stdout.strip())
        }

    except Exception as e:
        # return Response({
        #     "error": "Unexpected error",
        #     "details": str(e)
        # }, status=500)
        raise Exception({
            "error": "Unexpected error",
            "details": str(e)
        })

def invoke_update_order_status(order_id, status, timestamp):
    fabric_env = get_fabric_env()
    
    args_json = json.dumps({
        "Args": [order_id, status, timestamp]
    })

    print("🔧 Executing:", UPDATE_DOCS_SCRIPT_PATH, args_json)

    result = subprocess.run(
        [str(UPDATE_DOCS_SCRIPT_PATH), args_json],
        capture_output=True,
        text=True,
        env=fabric_env
    )

    print("✅ STDOUT:", result.stdout)
    # print("❌ STDERR:", result.stderr)

    if result.returncode != 0:
        raise Exception(f"Invoke script failed:\n{result.stderr}")