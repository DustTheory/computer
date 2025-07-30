package main

import (
	"fmt"
	"log"
	"math/rand"
	"time"

	"go.bug.st/serial"
)

func main() {
	const serialPortName = "/dev/ttyUSB1"
	const baudRate = 115200
	const bytesToSendPerChunk = 64
	const sendIntervalMs = 10

	mode := &serial.Mode{
		BaudRate: baudRate,
		DataBits: 8,
		Parity:   serial.NoParity,
		StopBits: serial.OneStopBit,
	}

	port, err := serial.Open(serialPortName, mode)
	if err != nil {
		log.Fatalf("Failed to open serial port %s: %v", serialPortName, err)
	}
	defer port.Close()

	fmt.Printf("--- Connected to %s at %d baud ---\n", serialPortName, baudRate)
	fmt.Println("Press Ctrl+C to stop streaming.")

	// time.Sleep(100 * time.Millisecond)

	rand.Seed(time.Now().UnixNano())

	for {
		dataToSend := make([]byte, bytesToSendPerChunk)

		for i := 0; i < bytesToSendPerChunk; i++ {
			dataToSend[i] = byte(rand.Intn(256))
		}

		n, err := port.Write(dataToSend)
		if err != nil {
			log.Printf("Error writing to serial port: %v", err)
		} else {
			fmt.Printf("Sent %d random bytes.\n", n)
		}

		// time.Sleep(sendIntervalMs * time.Millisecond)
	}
}
