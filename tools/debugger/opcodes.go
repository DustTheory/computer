package main

// OpCode represents a debug peripheral opcode
type OpCode byte

const (
	op_NOP            OpCode = 0x0
	op_RESET          OpCode = 0x1
	op_UNRESET        OpCode = 0x2
	op_HALT           OpCode = 0x3
	op_UNHALT         OpCode = 0x4
	op_PING           OpCode = 0x5
	op_READ_PC        OpCode = 0x6
	op_WRITE_PC       OpCode = 0x7
	op_READ_REGISTER  OpCode = 0x8
	op_WRITE_REGISTER OpCode = 0x9
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
	case op_READ_PC:
		return "READ_PC"
	case op_WRITE_PC:
		return "WRITE_PC"
	case op_READ_REGISTER:
		return "READ_REGISTER"
	case op_WRITE_REGISTER:
		return "WRITE_REGISTER"
	default:
		return "UNKNOWN"
	}
}
