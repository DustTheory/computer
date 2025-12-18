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
	CmdReadRegister:  {"Read Register", "Read a specific register value", false},
	CmdFullDump:      {"Full Dump", "Read all registers and memory", false},
	CmdPing:          {"Ping CPU", "Check if CPU is responsive", true},
	CmdSetRegister:   {"Set Register", "Write value to a register", false},
	CmdJumpToAddress: {"Jump to Address", "Set PC to specific address", false},
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
	default:
		return 0, false
	}
}

// GetName returns the display name for a command
func (c Command) GetName() string {
	if info, ok := commands[c]; ok {
		return info.name
	}
	return "Unknown"
}
