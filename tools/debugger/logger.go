package main

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"time"
)

// SetupLogger creates a logger that writes to a file
func SetupLogger() (*log.Logger, *os.File, error) {
	// Create logs directory if it doesn't exist
	logsDir := "logs"
	if err := os.MkdirAll(logsDir, 0755); err != nil {
		return nil, nil, fmt.Errorf("failed to create logs directory: %v", err)
	}

	// Create log file with timestamp
	timestamp := time.Now().Format("2006-01-02_15-04-05")
	logPath := filepath.Join(logsDir, fmt.Sprintf("debugger_%s.log", timestamp))

	logFile, err := os.OpenFile(logPath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to open log file: %v", err)
	}

	logger := log.New(logFile, "", log.LstdFlags|log.Lmicroseconds)
	logger.Printf("=== Debugger Session Started ===\n")

	return logger, logFile, nil
}
