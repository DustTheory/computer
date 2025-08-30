`include "../cpu_core_params.vh"

`ifndef CU_PARAMS_VH
`define CU_PARAMS_VH

localparam OP_J_TYPE = 7'b1101111;
localparam OP_B_TYPE = 7'b1100011;
localparam OP_S_TYPE = 7'b0100011;
localparam OP_R_TYPE = 7'b0110011;
localparam OP_U_TYPE_LUI = 7'b0110111;
localparam OP_U_TYPE_AUIPC = 7'b0010111;
localparam OP_I_TYPE_JALR = 7'b1100111;
localparam OP_I_TYPE_LOAD = 7'b0000011;
localparam OP_I_TYPE_ALU = 7'b0010011;
// localparam OP_I_TYPE_SYS   = 7'b1110011; // Syscall stuff, not implemented

localparam FUNC3_ALU_ADD_SUB = 3'b000;
localparam FUNC3_ALU_SLL = 3'b001;
localparam FUNC3_ALU_SLT = 3'b010;
localparam FUNC3_ALU_SLTU = 3'b011;
localparam FUNC3_ALU_XOR = 3'b100;
localparam FUNC3_ALU_SRL_SRA = 3'b101;
localparam FUNC3_ALU_OR = 3'b110;
localparam FUNC3_ALU_AND = 3'b111;

localparam FUNC3_LOAD_LB = 3'b000;
localparam FUNC3_LOAD_LH = 3'b001;
localparam FUNC3_LOAD_LW = 3'b010;
localparam FUNC3_LOAD_LBU = 3'b100;
localparam FUNC3_LOAD_LHU = 3'b101;

localparam FUNC3_BRANCH_BEQ = 3'b000;
localparam FUNC3_BRANCH_BNE = 3'b001;
localparam FUNC3_BRANCH_BLT = 3'b100;
localparam FUNC3_BRANCH_BGE = 3'b101;
localparam FUNC3_BRANCH_BLTU = 3'b110;
localparam FUNC3_BRANCH_BGEU = 3'b111;

`endif  // CU_PARAMS_VH
