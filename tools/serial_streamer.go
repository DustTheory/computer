package main

import (
	"fmt"
	"image"
	_ "image/jpeg"
	_ "image/png"
	"log"
	"os"

	"go.bug.st/serial"
)

const targetWidth = 640
const targetHeight = 480

type OpCode byte

const (
	op_RED   OpCode = 0x01
	op_GREEN OpCode = 0x02
	op_BLUE  OpCode = 0x03
	op_FRAME OpCode = 0x04
)

func main() {
	f, err := os.Open("./test_images/house_640x480.jpeg")
	if err != nil {
		fmt.Println("Failed to open image file:", err)
		return
	}
	defer f.Close()

	img, format, err := image.Decode(f)
	if err != nil {
		fmt.Println("Failed to decode image file:", err)
		return
	}

	fmt.Printf("Detected image format: %s\n", format)

	currentBounds := img.Bounds()
	if currentBounds.Dx() != targetWidth || currentBounds.Dy() != targetHeight {
		fmt.Printf("Warning: Image size %dx%d does not match assumed %dx%d. Proceeding anyway.\n",
			currentBounds.Dx(), currentBounds.Dy(), targetWidth, targetHeight)
	}

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
	defer port.Close()

	fmt.Printf("--- Connected to %s at %d baud ---\n", serialPortName, baudRate)
	fmt.Println("Press Ctrl+C to stop streaming.")

	var opCode OpCode = op_FRAME
	var packet []byte

	if opCode == op_FRAME {
		packet = make([]byte, targetWidth*targetHeight+1)
		packet[0] = byte(opCode)

		for y := 0; y < targetHeight; y++ {
			for x := 0; x < targetWidth; x++ {
				r, g, b, _ := img.At(x, y).RGBA()

				packet[y*targetWidth+x+1] = byte((r + g*2 + b) / 16384)
				if packet[y*targetWidth+x+1] > 15 {
					fmt.Printf("Warning: Pixel value %d at (%d,%d) exceeds 4-bit max. Clamping to 15.\n", packet[y*targetWidth+x+1], x, y)
					packet[y*targetWidth+x+1] = 15
				}
			}
		}
	} else {
		packet = []byte{byte(opCode)}
	}

	n, err := port.Write(packet)
	if err != nil {
		log.Printf("Error writing to serial port: %v", err)
	} else {
		fmt.Printf("Sent %d bytes.\n", n)
	}

}
