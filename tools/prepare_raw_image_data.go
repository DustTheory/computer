// package main

// import (
// 	"fmt"
// 	"image"
// 	_ "image/jpeg"
// 	_ "image/png"
// 	"os"
// 	"strconv"
// )

// const targetWidth = 640
// const targetHeight = 480

// func main() {
// 	f, err := os.Open("./test_images/house_640x480.jpeg")
// 	if err != nil {
// 		fmt.Println("Failed to open image file:", err)
// 		return
// 	}
// 	defer f.Close()

// 	img, format, err := image.Decode(f)
// 	if err != nil {
// 		fmt.Println("Failed to decode image file:", err)
// 		return
// 	}
// 	fmt.Printf("Detected image format: %s\n", format)

// 	currentBounds := img.Bounds()
// 	if currentBounds.Dx() != targetWidth || currentBounds.Dy() != targetHeight {
// 		fmt.Printf("Warning: Image size %dx%d does not match assumed %dx%d. Proceeding anyway.\n",
// 			currentBounds.Dx(), currentBounds.Dy(), targetWidth, targetHeight)
// 	}

// 	outputFile, err := os.Create("image_data.mem")
// 	if err != nil {
// 		fmt.Println("Failed to create .mem file:", err)
// 		return
// 	}
// 	defer outputFile.Close()

// 	for y := 0; y < targetHeight; y++ {
// 		for x := 0; x < targetWidth; x++ {
// 			r, g, b, _ := img.At(x, y).RGBA()

// 			r_bit := 0
// 			if r > 32767 {
// 				r_bit = 1
// 			}
// 			g_bit := 0
// 			if g > 32767 {
// 				g_bit = 1
// 			}
// 			b_bit := 0
// 			if b > 32767 {
// 				b_bit = 1
// 			}

// 			pixelValue := (r_bit << 2) | (g_bit << 1) | b_bit

// 			_, err := outputFile.WriteString(strconv.FormatInt(int64(pixelValue), 16) + "\n")
// 			if err != nil {
// 				fmt.Println("Failed to write to .mem file:", err)
// 				return
// 			}
// 		}
// 	}

// 	fmt.Printf("Successfully converted image to %s\n", outputFile.Name())
// }
