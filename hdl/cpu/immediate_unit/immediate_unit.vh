`include "cpu_core_params.vh"

`ifndef IMM_PARAMS_VH
`define IMM_PARAMS_VH

// All immediate types from the RISC-V spec
parameter [IMM_SEL_WIDTH:0] IMM_U_TYPE = 0;
parameter [IMM_SEL_WIDTH:0] IMM_B_TYPE = 1;
parameter [IMM_SEL_WIDTH:0] IMM_I_TYPE = 2;
parameter [IMM_SEL_WIDTH:0] IMM_J_TYPE = 3;
parameter [IMM_SEL_WIDTH:0] IMM_S_TYPE = 4;
parameter [IMM_SEL_WIDTH:0] IMM_UNKNOWN_TYPE = 5;

`endif  // IMM_PARAMS_VH
