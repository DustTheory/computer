`include "../cpu_core_params.vh"

`ifndef ALU_PARAMS_VH
`define ALU_PARAMS_VH

// ALU operation selects
localparam [ALU_SEL_WIDTH:0] ALU_SEL_ADD = 0;
localparam [ALU_SEL_WIDTH:0] ALU_SEL_SUB = 1;
localparam [ALU_SEL_WIDTH:0] ALU_SEL_AND = 2;
localparam [ALU_SEL_WIDTH:0] ALU_SEL_OR = 3;
localparam [ALU_SEL_WIDTH:0] ALU_SEL_XOR = 4;
localparam [ALU_SEL_WIDTH:0] ALU_SEL_SLL = 5;
localparam [ALU_SEL_WIDTH:0] ALU_SEL_SRL = 6;
localparam [ALU_SEL_WIDTH:0] ALU_SEL_SRA = 7;
localparam [ALU_SEL_WIDTH:0] ALU_SEL_UNKNOWN = 8;


`endif  // ALU_PARAMS_VH
