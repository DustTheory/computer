package main

import (
	"fmt"
	"os"

	tea "github.com/charmbracelet/bubbletea"
)

func main() {
	// Setup logging
	logger, logFile, err := SetupLogger()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to setup logger: %v\n", err)
		os.Exit(1)
	}
	defer logFile.Close()

	// Create serial manager
	serialMgr := NewSerialManager(logger)
	defer serialMgr.Close()

	// Create and run TUI
	p := tea.NewProgram(
		initialModel(serialMgr),
		tea.WithAltScreen(),
	)

	if _, err := p.Run(); err != nil {
		fmt.Fprintf(os.Stderr, "Error running program: %v\n", err)
		os.Exit(1)
	}
}
