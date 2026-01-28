package main

// Command represents a debug command
type Command int

const (
	CmdHalt Command = iota
	CmdUnhalt
	CmdReset
	CmdUnreset
	CmdReadRegister
	CmdFullDump
	CmdPing
	CmdReadPC
	CmdSetRegister
	CmdJumpToAddress
	CmdLoadProgram
	CmdStatsDump
	CmdReadMemory
	CmdWriteMemory
)

// CommandInfo holds display information about a command
type CommandInfo struct {
	name        string
	description string
	implemented bool
}

var commands = map[Command]CommandInfo{
	CmdHalt:          {"Halt CPU", "Stop CPU execution", true},
	CmdUnhalt:        {"Unhalt CPU", "Resume CPU execution", true},
	CmdReset:         {"Reset CPU", "Reset the CPU", true},
	CmdUnreset:       {"Unreset CPU", "Take CPU out of reset", true},
	CmdReadRegister:  {"Read Register", "Read a specific register value (CPU stays halted)", true},
	CmdFullDump:      {"Full Dump", "Read all registers and memory", false},
	CmdPing:          {"Ping CPU", "Check if CPU is responsive", true},
	CmdReadPC:        {"Read PC", "Read program counter value", true},
	CmdSetRegister:   {"Set Register", "Write value to a register (CPU stays halted)", true},
	CmdJumpToAddress: {"Jump to Address", "Set PC to specific address (CPU stays halted)", true},
	CmdLoadProgram:   {"Load Program", "Load program from file", false},
	CmdStatsDump:     {"Read Stats", "Read CPU statistics", false},
	CmdReadMemory:    {"Read Memory", "Read memory at address", false},
	CmdWriteMemory:   {"Write Memory", "Write to memory address", false},
}

// GetOpCode returns the opcode for a command
func (c Command) GetOpCode() (OpCode, bool) {
	switch c {
	case CmdHalt:
		return op_HALT, true
	case CmdUnhalt:
		return op_UNHALT, true
	case CmdReset:
		return op_RESET, true
	case CmdUnreset:
		return op_UNRESET, true
	case CmdPing:
		return op_PING, true
	case CmdReadPC:
		return op_READ_PC, true
	case CmdReadRegister:
		return op_READ_REGISTER, true
	case CmdSetRegister:
		return op_WRITE_REGISTER, true
	case CmdJumpToAddress:
		return op_WRITE_PC, true
	default:
		return 0, false
	}
}

// NeedsInput returns true if the command requires user input
func (c Command) NeedsInput() bool {
	switch c {
	case CmdReadRegister, CmdSetRegister, CmdJumpToAddress:
		return true
	default:
		return false
	}
}

// GetInputPrompt returns the prompt for user input
func (c Command) GetInputPrompt() string {
	switch c {
	case CmdReadRegister:
		return "Register number (0-31): "
	case CmdSetRegister:
		return "Register number (0-31): "
	case CmdJumpToAddress:
		return "Address (hex, e.g. 1000): "
	default:
		return ""
	}
}

// GetName returns the display name for a command
func (c Command) GetName() string {
	if info, ok := commands[c]; ok {
		return info.name
	}
	return "Unknown"
}
