`ifndef CPU_CORE_PARAMS_VH
`define CPU_CORE_PARAMS_VH

parameter XLEN = 32;  // Register width
parameter REG_ADDR_WIDTH = $clog2(XLEN);  // Register address width

// Bit widths for various selects and operation codes
localparam OP_CODE_WIDTH = 6;
localparam FUNC3_WIDTH = 2;
localparam FUNC7_WIDTH = 6;
localparam ALU_SEL_WIDTH = 4;
localparam CMP_SEL_WIDTH = 3;
localparam IMM_SEL_WIDTH = 3;
localparam LS_SEL_WIDTH = 4;
localparam MEMORY_STATE_WIDTH = 2;

// Control signals for what to write to the register file
localparam REG_WRITE_ALU = 0;
localparam REG_WRITE_CU = 1;
localparam REG_WRITE_IMM = 2;
localparam REG_WRITE_PC_NEXT = 3;
localparam REG_WRITE_DMEM = 4;
localparam REG_WRITE_NONE = 5;

localparam CLOCK_FREQUENCY = 81_247_969;

// Memory map constants
localparam CPU_BASE_ADDR = 32'h80000000;
localparam ROM_SIZE = 32'h00001000;
localparam ROM_BOUNDARY_ADDR = CPU_BASE_ADDR + ROM_SIZE - 1;
localparam FRAMEBUFFER_0_ADDR = 32'h87F1E000;
localparam FRAMEBUFFER_1_ADDR = 32'h87F8F000;
localparam FRAMEBUFFER_SIZE = 32'h71000;

// UART parameters
localparam UART_BAUD_RATE = 115200;
localparam UART_CLOCKS_PER_BIT = (CLOCK_FREQUENCY / UART_BAUD_RATE);

`endif  // CPU_CORE_PARAMS_VH
