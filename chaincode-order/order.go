package main

import (
	"encoding/json"
	"fmt"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

type SmartContract struct {
	contractapi.Contract
}

type Order struct {
	ID           string `json:"ID"`
	Status       string `json:"Status"`
	Timestamp    string `json:"Timestamp"`
	// DocumentHash string `json:"DocumentHash"`
}

func (s *SmartContract) CreateOrder(ctx contractapi.TransactionContextInterface, id, status, timestamp, docHash string) error {
	order := Order{
		ID:           id,
		Status:       status,
		Timestamp:    timestamp,
		// DocumentHash: docHash,
	}
	orderJSON, err := json.Marshal(order)
	if err != nil {
		return err
	}
	return ctx.GetStub().PutState(id, orderJSON)
}

func (s *SmartContract) ReadOrder(ctx contractapi.TransactionContextInterface, id string) (*Order, error) {
	orderJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return nil, fmt.Errorf("failed to read order: %v", err)
	}
	if orderJSON == nil {
		return nil, fmt.Errorf("order %s not found", id)
	}
	var order Order
	err = json.Unmarshal(orderJSON, &order)
	if err != nil {
		return nil, err
	}
	return &order, nil
}

func (s *SmartContract) InitLedger(ctx contractapi.TransactionContextInterface) error {
	return nil
}

func main() {
	cc, err := contractapi.NewChaincode(new(SmartContract))
	if err != nil {
		panic("Error creating chaincode: " + err.Error())
	}
	if err := cc.Start(); err != nil {
		panic("Error starting chaincode: " + err.Error())
	}
}
