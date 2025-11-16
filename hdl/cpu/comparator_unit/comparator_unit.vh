`include "cpu_core_params.vh"

`ifndef CMP_PARAMS_VH
`define CMP_PARAMS_VH

// Comparison types for the comparator unit
parameter [CMP_SEL_WIDTH:0] CMP_SEL_EQ = 0;
parameter [CMP_SEL_WIDTH:0] CMP_SEL_NE = 1;
parameter [CMP_SEL_WIDTH:0] CMP_SEL_LTU = 2;
parameter [CMP_SEL_WIDTH:0] CMP_SEL_GEU = 3;
parameter [CMP_SEL_WIDTH:0] CMP_SEL_LT = 4;
parameter [CMP_SEL_WIDTH:0] CMP_SEL_GE = 5;
parameter [CMP_SEL_WIDTH:0] CMP_SEL_UNKNOWN = 6;

`endif  // CMP_PARAMS_VH
