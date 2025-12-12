
`ifndef DEBUG_PERIPHERAL_VH
`define DEBUG_PERIPHERAL_VH

localparam s_IDLE = 2'd0;
localparam s_DECODE_AND_EXECUTE = 2'd1;

localparam op_NOP = 0'h00;
localparam op_RESET = 0'h01;
localparam op_UNRESET = 0'h02;
localparam op_HALT = 0'h03;
localparam op_UNHALT = 0'h04;
// localparam op_READ_REGISTER = 8'h05;

`endif  // DEBUG_PERIPHERAL_VH
