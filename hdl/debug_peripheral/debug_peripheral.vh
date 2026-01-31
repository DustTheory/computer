
`ifndef DEBUG_PERIPHERAL_VH
`define DEBUG_PERIPHERAL_VH

localparam s_IDLE = 2'd0;
localparam s_DECODE_AND_EXECUTE = 2'd1;

localparam op_NOP = 8'h00;
localparam op_RESET = 8'h01;
localparam op_UNRESET = 8'h02;
localparam op_HALT = 8'h03;
localparam op_UNHALT = 8'h04;
localparam op_PING = 8'h05;
localparam op_READ_PC = 8'h06;
localparam op_WRITE_PC = 8'h07;
localparam op_READ_REGISTER = 8'h08;
localparam op_WRITE_REGISTER = 8'h09;
localparam op_READ_MEMORY = 8'h0A;
localparam op_WRITE_MEMORY = 8'h0B;


localparam MEMORY_READ_ERROR_STRING = 32'hB00B1E55;
localparam MEMORY_WRITE_ERROR_STRING = 32'hABADBABE;
localparam PING_RESPONSE_BYTE = 8'hAA;

`endif  // DEBUG_PERIPHERAL_VH
