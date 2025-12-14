package main

import (
	"fmt"
	_ "image/jpeg"
	_ "image/png"
	"log"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"go.bug.st/serial"
)

type OpCode byte

const (
	op_NOP     OpCode = 0x0
	op_RESET   OpCode = 0x1
	op_UNRESET OpCode = 0x2
	op_HALT    OpCode = 0x3
	op_UNHALT  OpCode = 0x4
	op_PING    OpCode = 0x5
)

func main() {

	const serialPortName = "/dev/ttyUSB1"
	const baudRate = 115200

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

	// Use a channel to gracefully stop the reader goroutine
	done := make(chan struct{})
	// Use a channel to signal when the reader is ready
	ready := make(chan struct{})

	// Start the read goroutine — read raw bytes (not line-delimited)
	go func() {
		defer close(done)
		// Signal that reader is ready to receive data
		close(ready)
		buf := make([]byte, 64)
		for {
			n, err := port.Read(buf)
			if err != nil {
				// Ignore benign timeout and port-closed errors; otherwise log
				if err.Error() == "serial: read timeout" {
					return
				}
				if strings.Contains(strings.ToLower(err.Error()), "closed") {
					// expected when we close the port to shutdown
					return
				}
				log.Printf("Read error: %v", err)
				return
			}
			if n > 0 {
				// Print raw bytes in hex and ASCII where printable
				out := buf[:n]
				// Hex view
				hexParts := make([]string, len(out))
				for i, b := range out {
					hexParts[i] = fmt.Sprintf("0x%02X", b)
				}
				fmt.Printf("Received %d bytes: %s\n", n, strings.Join(hexParts, " "))
				// ASCII view (printable characters only)
				ascii := make([]byte, n)
				for i, b := range out {
					if b >= 32 && b <= 126 {
						ascii[i] = b
					} else {
						ascii[i] = '.'
					}
				}
				fmt.Printf("ASCII: %s\n", string(ascii))
			}
		}
	}()

	fmt.Printf("--- Connected to %s at %d baud ---\n", serialPortName, baudRate)
	fmt.Println("Press Ctrl+C to stop streaming.")

	// Wait until the reader goroutine has created its reader so we don't miss a fast reply
	<-ready

	// Send an initial ping
	n, err := port.Write([]byte{byte(op_RESET)})
	if err != nil {
		log.Printf("Error writing to serial port: %v", err)
	} else {
		fmt.Printf("Sent %d bytes.\n", n)
	}

	// Give the peripheral a short moment to process the unreset
	time.Sleep(50 * time.Millisecond)

	// Send ping
	n, err = port.Write([]byte{byte(op_PING)})
	if err != nil {
		log.Printf("Error writing ping to serial port: %v", err)
	} else {
		fmt.Printf("Sent ping (%d bytes).\n", n)
	}

	// Wait for interrupt (Ctrl+C) or termination and then shut down gracefully.
	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)
	<-sigs
	fmt.Println("\nSignal received, shutting down...")

	// Close the port to unblock the reader goroutine and wait for it.
	_ = port.Close()
	<-done

}
