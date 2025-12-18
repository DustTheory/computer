package main

// OpCode represents a debug peripheral opcode
type OpCode byte

const (
	op_NOP     OpCode = 0x0
	op_RESET   OpCode = 0x1
	op_UNRESET OpCode = 0x2
	op_HALT    OpCode = 0x3
	op_UNHALT  OpCode = 0x4
	op_PING    OpCode = 0x5
)

// String returns the human-readable name of the opcode
func (o OpCode) String() string {
	switch o {
	case op_NOP:
		return "NOP"
	case op_RESET:
		return "RESET"
	case op_UNRESET:
		return "UNRESET"
	case op_HALT:
		return "HALT"
	case op_UNHALT:
		return "UNHALT"
	case op_PING:
		return "PING"
	default:
		return "UNKNOWN"
	}
}
