`include "../cpu_core_params.vh"

`ifndef MEMORY_PARAMS_VH
`define MEMORY_PARAMS_VH

// Load/Store types
parameter [LS_SEL_WIDTH:0] LS_TYPE_LOAD_WORD = 0;
parameter [LS_SEL_WIDTH:0] LS_TYPE_LOAD_HALF = 1;
parameter [LS_SEL_WIDTH:0] LS_TYPE_LOAD_HALF_UNSIGNED = 2;
parameter [LS_SEL_WIDTH:0] LS_TYPE_LOAD_BYTE = 3;
parameter [LS_SEL_WIDTH:0] LS_TYPE_LOAD_BYTE_UNSIGNED = 4;
parameter [LS_SEL_WIDTH:0] LS_TYPE_STORE_WORD = 5;
parameter [LS_SEL_WIDTH:0] LS_TYPE_STORE_HALF = 6;
parameter [LS_SEL_WIDTH:0] LS_TYPE_STORE_BYTE = 7;
parameter [LS_SEL_WIDTH:0] LS_TYPE_NONE = 8;

`endif  // MEMORY_PARAMS_VH
