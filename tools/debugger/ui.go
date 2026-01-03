package main

import (
	"fmt"
	"strings"
	"time"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

// AppState represents the current state of the application
type AppState int

const (
	StateSelectPort AppState = iota
	StateMainMenu
)

// CPUState tracks the current state of the CPU
type CPUState struct {
	haltSet   bool
	resetSet  bool
	lastPing  time.Time
	connected bool
}

// Model represents the TUI state
type model struct {
	state          AppState
	availablePorts []string
	portCursor     int
	selectedPort   string
	commands       []Command
	cursor         int
	executing      bool
	status         string
	serialMgr      *SerialManager
	responses      []SerialResponse
	err            error
	width          int
	height         int
	scrollOffset   int  // Offset for scrolling through responses
	autoScroll     bool // Auto-scroll to latest response
	cpuState       CPUState
}

type portsListMsg struct {
	ports []string
}

type commandCompleteMsg struct {
	success bool
	message string
	cmd     Command
}

type serialDataMsg struct {
	response SerialResponse
}

type tickMsg time.Time

var (
	titleStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("86")).
			MarginTop(1).
			MarginBottom(1)

	selectedStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("170")).
			Bold(true).
			PaddingLeft(2)

	normalStyle = lipgloss.NewStyle().
			PaddingLeft(4)

	disabledStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("240")).
			PaddingLeft(4)

	statusStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("228")).
			MarginTop(1).
			MarginBottom(1)

	errorStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("196")).
			Bold(true)

	helpStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("241")).
			MarginTop(1)

	logBoxStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(lipgloss.Color("62")).
			Padding(0, 1).
			MarginTop(1)

	logEntryStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("245"))

	logEntryRecentStyle = lipgloss.NewStyle().
				Foreground(lipgloss.Color("255"))
)

func initialModel(serialMgr *SerialManager) model {
	cmdList := []Command{
		CmdHalt, CmdUnhalt, CmdReset, CmdUnreset,
		CmdPing, CmdReadRegister, CmdSetRegister,
		CmdJumpToAddress, CmdReadMemory, CmdWriteMemory,
		CmdFullDump, CmdStatsDump, CmdLoadProgram,
	}

	return model{
		state:        StateSelectPort,
		commands:     cmdList,
		cursor:       0,
		portCursor:   0,
		executing:    false,
		status:       "Select serial port",
		serialMgr:    serialMgr,
		responses:    make([]SerialResponse, 0),
		scrollOffset: 0,
		autoScroll:   true,
		cpuState: CPUState{
			haltSet:   false,
			resetSet:  false,
			connected: false,
		},
	}
}

func (m model) Init() tea.Cmd {
	return tea.Batch(
		listSerialPorts,
		tickCmd(),
	)
}

func tickCmd() tea.Cmd {
	return tea.Tick(100*time.Millisecond, func(t time.Time) tea.Msg {
		return tickMsg(t)
	})
}

func listSerialPorts() tea.Msg {
	ports := ListPorts()
	return portsListMsg{ports: ports}
}

func connectToPort(sm *SerialManager, portName string) tea.Cmd {
	return func() tea.Msg {
		err := sm.Connect(portName)
		if err != nil {
			return commandCompleteMsg{
				success: false,
				message: fmt.Sprintf("Failed to connect: %v", err),
			}
		}

		// Start listening for data
		sm.StartListening()

		msg := fmt.Sprintf("Connected to %s", portName)
		if portName == mockPortName {
			msg += " (mock mode)"
		}

		return commandCompleteMsg{
			success: true,
			message: msg,
		}
	}
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
		return m, nil

	case tickMsg:
		// Update responses from serial manager
		m.responses = m.serialMgr.GetResponses()
		return m, tickCmd()

	case portsListMsg:
		m.availablePorts = msg.ports
		if len(m.availablePorts) == 0 {
			m.status = "No serial ports found"
		} else {
			m.status = "Select serial port"
		}
		return m, nil

	case tea.KeyMsg:
		if m.executing {
			return m, nil
		}

		switch msg.String() {
		case "ctrl+c", "q":
			m.serialMgr.Close()
			return m, tea.Quit

		case "up", "k":
			if m.state == StateSelectPort {
				if m.portCursor > 0 {
					m.portCursor--
				}
			} else {
				if m.cursor > 0 {
					m.cursor--
				}
			}

		case "down", "j":
			if m.state == StateSelectPort {
				if m.portCursor < len(m.availablePorts)-1 {
					m.portCursor++
				}
			} else {
				if m.cursor < len(m.commands)-1 {
					m.cursor++
				}
			}

		// Scroll monitor with Ctrl+u/d (vim bindings)
		case "ctrl+u":
			if m.state == StateMainMenu {
				m.scrollOffset -= 10
				if m.scrollOffset < 0 {
					m.scrollOffset = 0
				}
				m.autoScroll = false
			}

		case "ctrl+d":
			if m.state == StateMainMenu {
				m.scrollOffset += 10
				maxScroll := len(m.responses) - 1
				if m.scrollOffset >= maxScroll {
					m.scrollOffset = maxScroll
					m.autoScroll = true // Re-enable auto-scroll at bottom
				} else {
					m.autoScroll = false
				}
			}

		// Scroll one line at a time with shift+j/k
		case "shift+up", "K":
			if m.state == StateMainMenu {
				if m.scrollOffset > 0 {
					m.scrollOffset--
				}
				m.autoScroll = false
			}

		case "shift+down", "J":
			if m.state == StateMainMenu {
				m.scrollOffset++
				maxScroll := len(m.responses) - 1
				if m.scrollOffset >= maxScroll {
					m.scrollOffset = maxScroll
					m.autoScroll = true
				} else {
					m.autoScroll = false
				}
			}

		// Jump to top/bottom with gg/G
		case "g":
			if m.state == StateMainMenu {
				m.scrollOffset = 0
				m.autoScroll = false
			}

		case "G":
			if m.state == StateMainMenu {
				m.scrollOffset = len(m.responses) - 1
				if m.scrollOffset < 0 {
					m.scrollOffset = 0
				}
				m.autoScroll = true
			}

		case "enter", " ":
			if m.state == StateSelectPort {
				if len(m.availablePorts) > 0 {
					m.selectedPort = m.availablePorts[m.portCursor]
					m.executing = true
					m.status = fmt.Sprintf("Connecting to %s...", m.selectedPort)
					return m, connectToPort(m.serialMgr, m.selectedPort)
				}
			} else if m.state == StateMainMenu {
				cmd := m.commands[m.cursor]
				if commands[cmd].implemented {
					m.executing = true
					m.status = fmt.Sprintf("Executing: %s...", commands[cmd].name)
					return m, m.executeCommand(cmd)
				}
			}
		}

	case commandCompleteMsg:
		m.executing = false
		if !msg.success {
			m.status = msg.message
			m.err = fmt.Errorf(msg.message)
		} else {
			if m.state == StateSelectPort {
				m.state = StateMainMenu
				m.cpuState.connected = true
			}
			m.status = msg.message
			m.err = nil
		}
	}

	return m, nil
}

func (m *model) updateCPUState(cmd Command) {
	switch cmd {
	case CmdHalt:
		m.cpuState.haltSet = true
	case CmdUnhalt:
		m.cpuState.haltSet = false
	case CmdReset:
		m.cpuState.resetSet = true
	case CmdUnreset:
		m.cpuState.resetSet = false
	case CmdPing:
		m.cpuState.lastPing = time.Now()
	}
}

func (m model) executeCommand(cmd Command) tea.Cmd {
	return func() tea.Msg {
		opcode, ok := cmd.GetOpCode()
		if !ok {
			return commandCompleteMsg{
				success: false,
				message: "Command not implemented",
			}
		}

		err := m.serialMgr.SendCommand(opcode)
		if err != nil {
			return commandCompleteMsg{
				success: false,
				message: fmt.Sprintf("Failed to send command: %v", err),
			}
		}

		// Wait a bit for response
		time.Sleep(150 * time.Millisecond)

		return commandCompleteMsg{
			success: true,
			message: fmt.Sprintf("✓ %s sent", cmd.GetName()),
		}
	}
}

func (m model) View() string {
	s := titleStyle.Render("🔧 CPU Debugger")
	s += "\n\n"

	if m.state == StateSelectPort {
		s += m.renderPortSelection()
	} else {
		s += m.renderMainMenu()
	}

	return s
}

func (m model) renderPortSelection() string {
	var s strings.Builder
	s.WriteString("Select Serial Port:\n\n")

	if len(m.availablePorts) == 0 {
		s.WriteString(disabledStyle.Render("No serial ports detected"))
		s.WriteString("\n\n")
		s.WriteString(helpStyle.Render("Press 'q' or ctrl+c to quit"))
	} else {
		for i, port := range m.availablePorts {
			cursor := "  "
			if m.portCursor == i {
				cursor = "▶ "
			}

			line := cursor + port

			if m.portCursor == i {
				s.WriteString(selectedStyle.Render(line) + "\n")
			} else {
				s.WriteString(normalStyle.Render(line) + "\n")
			}
		}

		s.WriteString("\n")
		if m.err != nil {
			s.WriteString(errorStyle.Render("Error: "+m.status) + "\n")
		} else {
			s.WriteString(statusStyle.Render("Status: "+m.status) + "\n")
		}

		s.WriteString(helpStyle.Render("\n↑/k up • ↓/j down • enter/space select • q/ctrl+c quit"))
	}

	return s.String()
}

func (m model) renderMainMenu() string {
	// Calculate split dimensions
	leftWidth := 40
	stateWidth := 28
	rightWidth := m.width - leftWidth - stateWidth - 6 // Account for borders and padding
	if rightWidth < 30 {
		rightWidth = 30
	}

	// Calculate available height (account for title, status, help)
	availableHeight := m.height - 6 // Reserve space for title and margins
	if availableHeight < 10 {
		availableHeight = 10
	}

	// Build left panel (commands)
	leftPanel := m.renderCommandPanel(leftWidth, availableHeight)

	// Build middle panel (CPU state)
	statePanel := m.renderCPUState(stateWidth, availableHeight)

	// Build right panel (serial monitor)
	rightPanel := m.renderSerialMonitor(rightWidth, availableHeight)

	// Combine panels side by side
	return lipgloss.JoinHorizontal(lipgloss.Top, leftPanel, statePanel, rightPanel)
}

func (m model) renderCommandPanel(width int, height int) string {
	var s strings.Builder

	panelStyle := lipgloss.NewStyle().
		Width(width).
		Height(height).
		Border(lipgloss.RoundedBorder()).
		BorderForeground(lipgloss.Color("62")).
		Padding(1)

	s.WriteString(lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("86")).Render("Commands"))
	s.WriteString("\n\n")

	// Commands list
	for i, cmd := range m.commands {
		info := commands[cmd]
		cursor := "  "
		if m.cursor == i {
			cursor = "▶ "
		}

		line := cursor + info.name

		if !info.implemented {
			line += " (not implemented)"
		}

		if m.cursor == i {
			s.WriteString(lipgloss.NewStyle().
				Foreground(lipgloss.Color("170")).
				Bold(true).
				Render(line) + "\n")
		} else if !info.implemented {
			s.WriteString(lipgloss.NewStyle().
				Foreground(lipgloss.Color("240")).
				Render(line) + "\n")
		} else {
			s.WriteString(line + "\n")
		}
	}

	// Status
	s.WriteString("\n")
	if m.err != nil {
		s.WriteString(errorStyle.Render("✗ "+m.status) + "\n")
	} else {
		s.WriteString(statusStyle.Render("✓ "+m.status) + "\n")
	}

	// Help
	s.WriteString("\n")
	s.WriteString(helpStyle.Render("↑/↓ select • ⏎ exec\nJ/K scroll • Ctrl+d/u page\ng/G top/bottom • q quit"))

	return panelStyle.Render(s.String())
}

func (m model) renderCPUState(width int, height int) string {
	var s strings.Builder

	panelStyle := lipgloss.NewStyle().
		Width(width).
		Height(height).
		Border(lipgloss.RoundedBorder()).
		BorderForeground(lipgloss.Color("62")).
		Padding(1)

	headerStyle := lipgloss.NewStyle().
		Bold(true).
		Foreground(lipgloss.Color("86"))

	s.WriteString(headerStyle.Render("⚙️  CPU State"))
	s.WriteString("\n\n")

	// Connection status
	connStatus := "❌ Disconnected"
	if m.cpuState.connected {
		connStatus = "✅ Connected"
	}
	s.WriteString(lipgloss.NewStyle().
		Foreground(lipgloss.Color("255")).
		Bold(true).
		Render(connStatus))
	s.WriteString("\n\n")

	// Halt flag
	haltIcon := "⚪"
	haltColor := lipgloss.Color("240")
	if m.cpuState.haltSet {
		haltIcon = "🔴"
		haltColor = lipgloss.Color("196")
	}
	s.WriteString(lipgloss.NewStyle().Foreground(haltColor).Render(haltIcon + " Halt: "))
	if m.cpuState.haltSet {
		s.WriteString(lipgloss.NewStyle().Foreground(lipgloss.Color("196")).Bold(true).Render("SET"))
	} else {
		s.WriteString(lipgloss.NewStyle().Foreground(lipgloss.Color("240")).Render("clear"))
	}
	s.WriteString("\n")

	// Reset flag
	resetIcon := "⚪"
	resetColor := lipgloss.Color("240")
	if m.cpuState.resetSet {
		resetIcon = "🔴"
		resetColor = lipgloss.Color("196")
	}
	s.WriteString(lipgloss.NewStyle().Foreground(resetColor).Render(resetIcon + " Reset: "))
	if m.cpuState.resetSet {
		s.WriteString(lipgloss.NewStyle().Foreground(lipgloss.Color("196")).Bold(true).Render("SET"))
	} else {
		s.WriteString(lipgloss.NewStyle().Foreground(lipgloss.Color("240")).Render("clear"))
	}
	s.WriteString("\n\n")

	// Last ping
	if !m.cpuState.lastPing.IsZero() {
		elapsed := time.Since(m.cpuState.lastPing)
		pingStr := fmt.Sprintf("🏓 Last ping: %s ago", formatDuration(elapsed))
		s.WriteString(lipgloss.NewStyle().Foreground(lipgloss.Color("245")).Render(pingStr))
	} else {
		s.WriteString(lipgloss.NewStyle().Foreground(lipgloss.Color("240")).Render("🏓 No ping yet"))
	}

	return panelStyle.Render(s.String())
}

func formatDuration(d time.Duration) string {
	if d < time.Second {
		return fmt.Sprintf("%dms", d.Milliseconds())
	}
	if d < time.Minute {
		return fmt.Sprintf("%.1fs", d.Seconds())
	}
	return fmt.Sprintf("%.1fm", d.Minutes())
}

func (m model) renderSerialMonitor(width int, height int) string {
	var content strings.Builder

	panelStyle := lipgloss.NewStyle().
		Width(width).
		Height(height).
		Border(lipgloss.RoundedBorder()).
		BorderForeground(lipgloss.Color("62")).
		Padding(1)

	headerStyle := lipgloss.NewStyle().
		Bold(true).
		Foreground(lipgloss.Color("86"))

	content.WriteString(headerStyle.Render("📡 Serial Monitor"))
	content.WriteString("\n\n")

	if len(m.responses) == 0 {
		content.WriteString(logEntryStyle.Render("(no data received yet)"))
	} else {
		// Calculate how many responses we can show based on height
		// Each response takes ~4 lines (timestamp + RX + parsed + blank)
		maxResponses := (height - 6) / 4 // Account for header, scroll indicator, padding
		if maxResponses < 3 {
			maxResponses = 3
		}

		// Auto-scroll to bottom if enabled
		if m.autoScroll {
			m.scrollOffset = len(m.responses) - 1
		}

		// Calculate visible window based on scroll offset
		end := m.scrollOffset + 1
		start := end - maxResponses
		if start < 0 {
			start = 0
		}
		if end > len(m.responses) {
			end = len(m.responses)
		}

		// Show scroll indicator
		if !m.autoScroll {
			scrollInfo := fmt.Sprintf("[Scroll: %d/%d] ", m.scrollOffset+1, len(m.responses))
			content.WriteString(lipgloss.NewStyle().Foreground(lipgloss.Color("240")).Render(scrollInfo))
		}
		if m.autoScroll {
			content.WriteString(lipgloss.NewStyle().Foreground(lipgloss.Color("green")).Render("[Auto-scroll ✓] "))
		}
		content.WriteString("\n")

		now := time.Now()
		for i := start; i < end; i++ {
			resp := m.responses[i]
			timestamp := resp.Timestamp.Format("15:04:05.000")
			age := now.Sub(resp.Timestamp)

			// Format with wrapping for narrow terminals
			timeStr := lipgloss.NewStyle().Foreground(lipgloss.Color("240")).Render(timestamp)

			rawStr := lipgloss.NewStyle().Foreground(lipgloss.Color("cyan")).Render(resp.Raw)
			parsedStr := lipgloss.NewStyle().Foreground(lipgloss.Color("green")).Render(resp.Parsed)

			line := fmt.Sprintf("%s\n  RX: %s\n  └─ %s\n", timeStr, rawStr, parsedStr)

			// Recent entries are brighter
			if age < 2*time.Second {
				content.WriteString(logEntryRecentStyle.Render(line))
			} else {
				content.WriteString(line)
			}
		}
	}

	return panelStyle.Render(content.String())
}
