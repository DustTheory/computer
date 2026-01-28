package main

import (
	"fmt"
	"log"
	"strings"
	"sync"
	"time"

	"go.bug.st/serial"
)

const (
	baudRate       = 115200
	mockPortName   = "[Mock Port - Testing Only]"
	readBufferSize = 64
)

// SerialResponse represents data received from the serial port
type SerialResponse struct {
	Timestamp time.Time
	Data      []byte
	Raw       string
	Parsed    string
}

// SerialManager manages serial port communication
type SerialManager struct {
	port        serial.Port
	portName    string
	isMock      bool
	responses   []SerialResponse
	mu          sync.RWMutex
	listeners   []chan SerialResponse
	stopChan    chan struct{}
	isListening bool
	logFile     *log.Logger
}

// NewSerialManager creates a new serial manager
func NewSerialManager(logger *log.Logger) *SerialManager {
	return &SerialManager{
		responses:   make([]SerialResponse, 0),
		listeners:   make([]chan SerialResponse, 0),
		stopChan:    make(chan struct{}),
		isListening: false,
		logFile:     logger,
	}
}

// ListPorts returns available serial ports
func ListPorts() []string {
	ports, err := serial.GetPortsList()
	if err != nil {
		return []string{mockPortName}
	}
	// Always add mock port option for testing
	return append([]string{mockPortName}, ports...)
}

// Connect opens a connection to the specified port
func (sm *SerialManager) Connect(portName string) error {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	sm.portName = portName
	sm.isMock = portName == mockPortName

	if sm.isMock {
		sm.logFile.Printf("Connected to mock port\n")
		return nil
	}

	mode := &serial.Mode{
		BaudRate: baudRate,
		DataBits: 8,
		Parity:   serial.NoParity,
		StopBits: serial.OneStopBit,
	}

	port, err := serial.Open(portName, mode)
	if err != nil {
		return fmt.Errorf("failed to open serial port: %v", err)
	}

	sm.port = port
	sm.logFile.Printf("Connected to %s at %d baud\n", portName, baudRate)
	return nil
}

// StartListening begins listening for serial data
func (sm *SerialManager) StartListening() {
	sm.mu.Lock()
	if sm.isListening {
		sm.mu.Unlock()
		return
	}
	sm.isListening = true
	sm.stopChan = make(chan struct{})
	sm.mu.Unlock()

	go sm.listenLoop()
}

// StopListening stops listening for serial data
func (sm *SerialManager) StopListening() {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	if !sm.isListening {
		return
	}

	close(sm.stopChan)
	sm.isListening = false
}

// listenLoop continuously reads from the serial port
func (sm *SerialManager) listenLoop() {
	buf := make([]byte, readBufferSize)

	for {
		select {
		case <-sm.stopChan:
			return
		default:
			if sm.isMock {
				time.Sleep(100 * time.Millisecond)
				continue
			}

			if sm.port == nil {
				time.Sleep(100 * time.Millisecond)
				continue
			}

			n, err := sm.port.Read(buf)
			if err != nil {
				// Handle timeout gracefully
				if strings.Contains(err.Error(), "timeout") {
					continue
				}
				sm.logFile.Printf("Read error: %v\n", err)
				time.Sleep(100 * time.Millisecond)
				continue
			}

			if n > 0 {
				data := make([]byte, n)
				copy(data, buf[:n])
				sm.handleResponse(data)
			}
		}
	}
}

// handleResponse processes received data
func (sm *SerialManager) handleResponse(data []byte) {
	response := SerialResponse{
		Timestamp: time.Now(),
		Data:      data,
		Raw:       formatHex(data),
		Parsed:    parseResponse(data),
	}

	sm.mu.Lock()
	sm.responses = append(sm.responses, response)
	// Keep only last 100 responses
	if len(sm.responses) > 100 {
		sm.responses = sm.responses[len(sm.responses)-100:]
	}
	sm.mu.Unlock()

	sm.logFile.Printf("RX: %s | Parsed: %s\n", response.Raw, response.Parsed)

	// Notify all listeners
	sm.mu.RLock()
	for _, listener := range sm.listeners {
		select {
		case listener <- response:
		default:
			// Don't block if listener is slow
		}
	}
	sm.mu.RUnlock()
}

// Subscribe returns a channel that receives serial responses
func (sm *SerialManager) Subscribe() chan SerialResponse {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	ch := make(chan SerialResponse, 10)
	sm.listeners = append(sm.listeners, ch)
	return ch
}

// GetResponses returns all stored responses
func (sm *SerialManager) GetResponses() []SerialResponse {
	sm.mu.RLock()
	defer sm.mu.RUnlock()

	result := make([]SerialResponse, len(sm.responses))
	copy(result, sm.responses)
	return result
}

// SendCommand sends a command to the serial port
func (sm *SerialManager) SendCommand(opcode OpCode) error {
	sm.logFile.Printf("TX: %s (0x%02X)\n", opcode.String(), opcode)

	if sm.isMock {
		// Simulate mock response
		time.AfterFunc(50*time.Millisecond, func() {
			mockData := []byte{byte(opcode), 0xAA, 0x55}
			sm.handleResponse(mockData)
		})
		return nil
	}

	if sm.port == nil {
		return fmt.Errorf("serial port not connected")
	}

	_, err := sm.port.Write([]byte{byte(opcode)})
	return err
}

// SendCommandWithData sends a command with additional data bytes
func (sm *SerialManager) SendCommandWithData(opcode OpCode, data []byte) error {
	dataStr := formatHex(data)
	sm.logFile.Printf("TX: %s (0x%02X) + data: %s\n", opcode.String(), opcode, dataStr)

	if sm.isMock {
		// Simulate mock response based on command type
		time.AfterFunc(50*time.Millisecond, func() {
			var mockData []byte
			switch opcode {
			case op_READ_REGISTER:
				// Return mock register value (4 bytes, little-endian)
				mockData = []byte{0x12, 0x34, 0x56, 0x78}
			case op_WRITE_REGISTER, op_WRITE_PC:
				// No response expected for write commands
				mockData = []byte{0xAA} // Just an ACK
			default:
				mockData = []byte{byte(opcode), 0xAA}
			}
			sm.handleResponse(mockData)
		})
		return nil
	}

	if sm.port == nil {
		return fmt.Errorf("serial port not connected")
	}

	// Send opcode first
	_, err := sm.port.Write([]byte{byte(opcode)})
	if err != nil {
		return err
	}

	// Small delay between opcode and data
	time.Sleep(10 * time.Millisecond)

	// Send data bytes
	_, err = sm.port.Write(data)
	return err
}

// Close closes the serial port
func (sm *SerialManager) Close() error {
	sm.StopListening()

	sm.mu.Lock()
	defer sm.mu.Unlock()

	if sm.port != nil {
		err := sm.port.Close()
		sm.port = nil
		return err
	}
	return nil
}

// formatHex formats bytes as hex string
func formatHex(data []byte) string {
	parts := make([]string, len(data))
	for i, b := range data {
		parts[i] = fmt.Sprintf("0x%02X", b)
	}
	return strings.Join(parts, " ")
}

// parseResponse attempts to parse the response data
func parseResponse(data []byte) string {
	if len(data) == 0 {
		return "Empty response"
	}

	// Check for PING response (single 0xAA byte)
	if len(data) == 1 && data[0] == 0xAA {
		return "PING response (0xAA)"
	}

	// Check for 4-byte value response (could be PC or register value)
	if len(data) == 4 {
		value := uint32(data[0]) |
			(uint32(data[1]) << 8) |
			(uint32(data[2]) << 16) |
			(uint32(data[3]) << 24)
		return fmt.Sprintf("0x%08X (%d)", value, value)
	}

	// Try to identify opcode echo
	if len(data) >= 1 {
		opcode := OpCode(data[0])
		if name := opcode.String(); name != "UNKNOWN" {
			if len(data) == 1 {
				return fmt.Sprintf("Echo: %s", name)
			}
			return fmt.Sprintf("Echo: %s + %d bytes", name, len(data)-1)
		}
	}

	return fmt.Sprintf("%d bytes", len(data))
}
