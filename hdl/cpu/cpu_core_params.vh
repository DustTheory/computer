`ifndef CPU_CORE_PARAMS_VH
`define CPU_CORE_PARAMS_VH

parameter XLEN = 32;  // Register width
parameter REG_ADDR_WIDTH = $clog2(XLEN);  // Register address width

// Bit widths for various selects
localparam ALU_SEL_WIDTH = 4;
localparam CMP_SEL_WIDTH = 3;
localparam IMM_SEL_WIDTH = 3;

// Control signals for what to write to the register file
localparam REG_WRITE_ALU = 0;
localparam REG_WRITE_CU = 1;
localparam REG_WRITE_IMM = 2;
localparam REG_WRITE_PC_NEXT = 3;
localparam REG_WRITE_DMEM = 4;
localparam REG_WRITE_NONE = 5;

`endif  // CPU_CORE_PARAMS_VH
