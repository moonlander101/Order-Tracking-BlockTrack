package main

import (
	"encoding/json"
	"errors"
	"fmt"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

type OrderType string

const (
	OrderTypeORD OrderType = "ORD"
	OrderTypeSR  OrderType = "SR"
)

type SmartContract struct {
	contractapi.Contract
}

type Order struct {
	ID             string     `json:"ID"`
	Status         string     `json:"Status"`
	Timestamp      string     `json:"Timestamp"`
	Type           OrderType  `json:"Type"`
	DocumentHashes []string   `json:"DocumentHashes"`
}

func isValidOrderType(t string) bool {
	return t == string(OrderTypeORD) || t == string(OrderTypeSR)
}

func (s *SmartContract) CreateOrder(ctx contractapi.TransactionContextInterface, id, status, timestamp, orderType string, docHashesJSON string) error {
	if !isValidOrderType(orderType) {
		return errors.New("invalid order type")
	}

	var docHashes []string
	if err := json.Unmarshal([]byte(docHashesJSON), &docHashes); err != nil {
		return fmt.Errorf("invalid document hash list: %v", err)
	}

	order := Order{
		ID:             id,
		Status:         status,
		Timestamp:      timestamp,
		Type:           OrderType(orderType),
		DocumentHashes: docHashes,
	}

	orderJSON, err := json.Marshal(order)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(id, orderJSON)
}

func contains(slice []string, item string) bool {
	for _, v := range slice {
		if v == item {
			return true
		}
	}
	return false
}

func (s *SmartContract) AddDocumentsToOrder(ctx contractapi.TransactionContextInterface, id string, docHashesJSON string) error {
	var newDocHashes []string
	if err := json.Unmarshal([]byte(docHashesJSON), &newDocHashes); err != nil {
		return fmt.Errorf("invalid document hash list: %v", err)
	}

	orderJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return fmt.Errorf("failed to read order: %v", err)
	}
	if orderJSON == nil {
		return fmt.Errorf("order %s not found", id)
	}

	var order Order
	if err := json.Unmarshal(orderJSON, &order); err != nil {
		return fmt.Errorf("failed to unmarshal order: %v", err)
	}

	for _, docHash := range newDocHashes {
		if !contains(order.DocumentHashes, docHash) {
			order.DocumentHashes = append(order.DocumentHashes, docHash)
		}
	}

	updatedOrderJSON, err := json.Marshal(order)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(id, updatedOrderJSON)
}

func remove(slice []string, item string) []string {
	for i, a := range slice {
		if a == item {
			// Remove it from the slice
			return append(slice[:i], slice[i+1:]...)
		}
	}
	return slice
}


func (s *SmartContract) DeleteDocumentsFromOrder(ctx contractapi.TransactionContextInterface, id string, docHashesJSON string) error {
	var docHashesToDelete []string
	if err := json.Unmarshal([]byte(docHashesJSON), &docHashesToDelete); err != nil {
		return fmt.Errorf("invalid document hash list: %v", err)
	}

	orderJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return fmt.Errorf("failed to read order: %v", err)
	}
	if orderJSON == nil {
		return fmt.Errorf("order %s not found", id)
	}

	var order Order
	if err := json.Unmarshal(orderJSON, &order); err != nil {
		return fmt.Errorf("failed to unmarshal order: %v", err)
	}

	for _, docHash := range docHashesToDelete {
		order.DocumentHashes = remove(order.DocumentHashes, docHash)
	}

	updatedOrderJSON, err := json.Marshal(order)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(id, updatedOrderJSON)
}

func (s *SmartContract) UpdateOrderStatus(ctx contractapi.TransactionContextInterface, id string, newStatus string) error {
	orderJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return fmt.Errorf("failed to read order: %v", err)
	}
	if orderJSON == nil {
		return fmt.Errorf("order %s not found", id)
	}

	var order Order
	if err := json.Unmarshal(orderJSON, &order); err != nil {
		return fmt.Errorf("failed to unmarshal order: %v", err)
	}

	order.Status = newStatus

	updatedOrderJSON, err := json.Marshal(order)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(id, updatedOrderJSON)
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
