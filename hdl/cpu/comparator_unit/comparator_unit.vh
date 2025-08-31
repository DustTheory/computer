`include "../cpu_core_params.vh"

`ifndef CMP_PARAMS_VH
`define CMP_PARAMS_VH

// Comparison types for the comparator unit
parameter [CMP_SEL_WIDTH:0] CMP_SEL_BEQ = 0;
parameter [CMP_SEL_WIDTH:0] CMP_SEL_BNE = 1;
parameter [CMP_SEL_WIDTH:0] CMP_SEL_BLTU = 2;
parameter [CMP_SEL_WIDTH:0] CMP_SEL_BGEU = 3;
parameter [CMP_SEL_WIDTH:0] CMP_SEL_BLT = 4;
parameter [CMP_SEL_WIDTH:0] CMP_SEL_BGE = 5;
parameter [CMP_SEL_WIDTH:0] CMP_SEL_UNKNOWN = 6;

`endif  // CMP_PARAMS_VH
