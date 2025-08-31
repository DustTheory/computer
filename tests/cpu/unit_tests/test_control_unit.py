import cocotb
from cocotb.triggers import Timer
from constants import (
    ALU_SEL_ADD,
    ALU_SEL_SUB,
    ALU_SEL_AND,
    ALU_SEL_OR,
    ALU_SEL_XOR,
    ALU_SEL_SLL,
    ALU_SEL_SRL,
    ALU_SEL_SRA,
    ALU_SEL_UNKNOWN,

    CMP_SEL_BEQ,
    CMP_SEL_BNE,
    CMP_SEL_BLTU,
    CMP_SEL_BGEU,
    CMP_SEL_BLT,
    CMP_SEL_BGE,
    CMP_SEL_UNKNOWN,

    IMM_U_TYPE,
    IMM_B_TYPE,
    IMM_I_TYPE,
    IMM_J_TYPE,
    IMM_S_TYPE,
    IMM_UNKNOWN_TYPE,

    LS_TYPE_LOAD_WORD,
    LS_TYPE_LOAD_HALF,
    LS_TYPE_LOAD_HALF_UNSIGNED,
    LS_TYPE_LOAD_BYTE,
    LS_TYPE_LOAD_BYTE_UNSIGNED,
    LS_TYPE_STORE_WORD,
    LS_TYPE_STORE_HALF,
    LS_TYPE_STORE_BYTE,
    LS_TYPE_NONE,

    REG_WRITE_ALU,
    REG_WRITE_CU,
    REG_WRITE_IMM,
    REG_WRITE_PC_NEXT,
    REG_WRITE_DMEM,
    REG_WRITE_NONE,
)

wait_ns = 1

OP_J_TYPE = 0b1101111
OP_B_TYPE = 0b1100011
OP_S_TYPE = 0b0100011
OP_R_TYPE = 0b0110011
OP_U_TYPE_LUI = 0b0110111
OP_U_TYPE_AUIPC = 0b0010111
OP_I_TYPE_JALR = 0b1100111
OP_I_TYPE_LOAD = 0b0000011
OP_I_TYPE_ALU = 0b0010011
# OP_I_TYPE_SYS = 0b1110011 // Syscall stuff, not implemented

FUNC3_ALU_ADD_SUB = 0b000
FUNC3_ALU_SLL = 0b001
FUNC3_ALU_SLT = 0b010
FUNC3_ALU_SLTU = 0b011
FUNC3_ALU_XOR = 0b100
FUNC3_ALU_SRL_SRA = 0b101
FUNC3_ALU_OR = 0b110
FUNC3_ALU_AND = 0b111

FUNC3_LOAD_LB = 0b000
FUNC3_LOAD_LH = 0b001
FUNC3_LOAD_LW = 0b010
FUNC3_LOAD_LBU = 0b100
FUNC3_LOAD_LHU = 0b101

FUNC3_BRANCH_BEQ = 0b000
FUNC3_BRANCH_BNE = 0b001
FUNC3_BRANCH_BLT = 0b100
FUNC3_BRANCH_BGE = 0b101
FUNC3_BRANCH_BLTU = 0b110
FUNC3_BRANCH_BGEU = 0b111


@cocotb.test()
async def test_r_type_instructions(dut):
    tests = [
        ("ADD", FUNC3_ALU_ADD_SUB, 0, ALU_SEL_ADD),
        ("SUB", FUNC3_ALU_ADD_SUB, 1, ALU_SEL_SUB),
        ("AND", FUNC3_ALU_AND, 0, ALU_SEL_AND),
        ("OR", FUNC3_ALU_OR, 0, ALU_SEL_OR),
        ("XOR", FUNC3_ALU_XOR, 0, ALU_SEL_XOR),
        ("SLL", FUNC3_ALU_SLL, 0, ALU_SEL_SLL),
        ("SRL", FUNC3_ALU_SRL_SRA, 0, ALU_SEL_SRL),
        ("SRA", FUNC3_ALU_SRL_SRA, 1, ALU_SEL_SRA),
    ]

    for name, funct3, funct7_bit5, expected_alu in tests:
        dut._log.info(f"Starting {name} instruction test")

        dut.control_unit.i_Op_Code.value = OP_R_TYPE
        dut.control_unit.i_Funct3.value = funct3
        dut.control_unit.i_Funct7_Bit_5.value = funct7_bit5
        dut.control_unit.i_Branch_Enable.value = 0

        await Timer(wait_ns, units='ns')
        assert dut.control_unit.o_Port_A_Select.value == 1, f"Port A Select mismatch for {name}: expected 1, got {dut.control_unit.o_Port_A_Select.value}"
        assert dut.control_unit.o_Port_B_Select.value == 1, f"Port B Select mismatch for {name}: expected 1, got {dut.control_unit.o_Port_B_Select.value}"
        assert dut.control_unit.o_Alu_Select.value == expected_alu, f"ALU Select mismatch for {name}: expected {expected_alu}, got {dut.control_unit.o_Alu_Select.value}"
        assert dut.control_unit.o_Cmp_Select.value == CMP_SEL_UNKNOWN, f"Comparator Select mismatch for {name}: expected {CMP_SEL_UNKNOWN}, got {dut.control_unit.o_Cmp_Select.value}"
        assert dut.control_unit.o_Imm_Select.value == IMM_UNKNOWN_TYPE, f"Immediate Select mismatch for {name}: expected {IMM_UNKNOWN_TYPE}, got {dut.control_unit.o_Imm_Select.value}"    
        assert dut.control_unit.o_Load_Store_Type.value == LS_TYPE_NONE, f"Load/Store Type mismatch for {name}: expected {LS_TYPE_NONE}, got {dut.control_unit.o_Load_Store_Type.value}"
        assert dut.control_unit.o_Reg_Write_Select.value == REG_WRITE_ALU, f"Reg Write Select mismatch for {name}: expected {REG_WRITE_ALU}, got {dut.control_unit.o_Reg_Write_Select.value}"
        assert dut.control_unit.o_Reg_Write_Enable.value == 1, f"Reg Write Enable mismatch for {name}: expected 1, got {dut.control_unit.o_Reg_Write_Enable.value}"
        assert dut.control_unit.o_Mem_Write_Enable.value == 0, f"Mem Write Enable mismatch for {name}: expected 0, got {dut.control_unit.o_Mem_Write_Enable.value}"
        assert dut.control_unit.o_Pc_Alu_Mux_Select.value == 0, f"PC ALU Mux Select mismatch for {name}: expected 0, got {dut.control_unit.o_Pc_Alu_Mux_Select.value}"
        dut._log.info(f"{name} instruction test passed")
        
@cocotb.test()
async def test_i_type_alu_instructions(dut):
    tests = [
        ("ADDI", FUNC3_ALU_ADD_SUB, 0,  ALU_SEL_ADD),
        ("ANDI", FUNC3_ALU_AND, 0, ALU_SEL_AND),
        ("ORI", FUNC3_ALU_OR, 0, ALU_SEL_OR),
        ("XORI", FUNC3_ALU_XOR, 0, ALU_SEL_XOR),
        ("SLLI", FUNC3_ALU_SLL, 0, ALU_SEL_SLL),
        ("SRLI", FUNC3_ALU_SRL_SRA, 0, ALU_SEL_SRL),
        ("SRAI", FUNC3_ALU_SRL_SRA, 1, ALU_SEL_SRA),
    ]

    for name, funct3, func7_bit5, expected_alu in tests:
        dut._log.info(f"Starting {name} instruction test")

        dut.control_unit.i_Op_Code.value = OP_I_TYPE_ALU
        dut.control_unit.i_Funct3.value = funct3
        dut.control_unit.i_Funct7_Bit_5.value = func7_bit5
        dut.control_unit.i_Branch_Enable.value = 0
        await Timer(wait_ns, units='ns')

        assert dut.control_unit.o_Port_A_Select.value == 1, f"Port A Select mismatch for {name}: expected 1, got {dut.control_unit.o_Port_A_Select.value}"
        assert dut.control_unit.o_Port_B_Select.value == 0, f"Port B Select mismatch for {name}: expected 0, got {dut.control_unit.o_Port_B_Select.value}"
        assert dut.control_unit.o_Alu_Select.value == expected_alu, f"ALU Select mismatch for {name}: expected {expected_alu}, got {dut.control_unit.o_Alu_Select.value}"
        assert dut.control_unit.o_Cmp_Select.value == CMP_SEL_UNKNOWN, f"Comparator Select mismatch for {name}: expected {CMP_SEL_UNKNOWN}, got {dut.control_unit.o_Cmp_Select.value}"
        assert dut.control_unit.o_Imm_Select.value == IMM_I_TYPE, f"Immediate Select mismatch for {name}: expected {IMM_I_TYPE}, got {dut.control_unit.o_Imm_Select.value}"
        assert dut.control_unit.o_Load_Store_Type.value == LS_TYPE_NONE, f"Load/Store Type mismatch for {name}: expected {LS_TYPE_NONE}, got {dut.control_unit.o_Load_Store_Type.value}"
        assert dut.control_unit.o_Reg_Write_Select.value == REG_WRITE_ALU, f"Reg Write Select mismatch for {name}: expected {REG_WRITE_ALU}, got {dut.control_unit.o_Reg_Write_Select.value}"
        assert dut.control_unit.o_Reg_Write_Enable.value == 1, f"Reg Write Enable mismatch for {name}: expected 1, got {dut.control_unit.o_Reg_Write_Enable.value}"
        assert dut.control_unit.o_Mem_Write_Enable.value == 0, f"Mem Write Enable mismatch for {name}: expected 0, got {dut.control_unit.o_Mem_Write_Enable.value}"
        assert dut.control_unit.o_Pc_Alu_Mux_Select.value == 0, f"PC ALU Mux Select mismatch for {name}: expected 0, got {dut.control_unit.o_Pc_Alu_Mux_Select.value}"
        dut._log.info(f"{name} instruction test passed")

@cocotb.test()
async def test_branch_instructions(dut):
    tests = [
        ("BEQ", FUNC3_BRANCH_BEQ, CMP_SEL_BEQ),
        ("BNE", FUNC3_BRANCH_BNE, CMP_SEL_BNE),
        ("BLT", FUNC3_BRANCH_BLT, CMP_SEL_BLT),
        ("BGE", FUNC3_BRANCH_BGE, CMP_SEL_BGE),
        ("BLTU", FUNC3_BRANCH_BLTU, CMP_SEL_BLTU),
        ("BGEU", FUNC3_BRANCH_BGEU, CMP_SEL_BGEU),
    ]

    for name, funct3, expected_cmp in tests:
        dut._log.info(f"Starting {name} instruction test")

        dut.control_unit.i_Op_Code.value = OP_B_TYPE
        dut.control_unit.i_Funct3.value = funct3
        dut.control_unit.i_Funct7_Bit_5.value = 0
        dut.control_unit.i_Branch_Enable.value = 1
        await Timer(wait_ns, units='ns')

        assert dut.control_unit.o_Port_A_Select.value == 0, f"Port A Select mismatch for {name}: expected 0, got {dut.control_unit.o_Port_A_Select.value}"
        assert dut.control_unit.o_Port_B_Select.value == 0, f"Port B Select mismatch for {name}: expected 0, got {dut.control_unit.o_Port_B_Select.value}"  
        assert dut.control_unit.o_Alu_Select.value == ALU_SEL_ADD, f"ALU Select mismatch for {name}: expected {ALU_SEL_UNKNOWN}, got {dut.control_unit.o_Alu_Select.value}"
        assert dut.control_unit.o_Cmp_Select.value == expected_cmp, f"Comparator Select mismatch for {name}: expected {expected_cmp}, got {dut.control_unit.o_Cmp_Select.value}"
        assert dut.control_unit.o_Imm_Select.value == IMM_B_TYPE, f"Immediate Select mismatch for {name}: expected {IMM_B_TYPE}, got {dut.control_unit.o_Imm_Select.value}"
        assert dut.control_unit.o_Load_Store_Type.value == LS_TYPE_NONE, f"Load/Store Type mismatch for {name}: expected {LS_TYPE_NONE}, got {dut.control_unit.o_Load_Store_Type.value}"
        assert dut.control_unit.o_Reg_Write_Select.value == REG_WRITE_NONE, f"Reg Write Select mismatch for {name}: expected {REG_WRITE_ALU}, got {dut.control_unit.o_Reg_Write_Select.value}"
        assert dut.control_unit.o_Reg_Write_Enable.value == 0, f"Reg Write Enable mismatch for {name}: expected 0, got {dut.control_unit.o_Reg_Write_Enable.value}"
        assert dut.control_unit.o_Mem_Write_Enable.value == 0, f"Mem Write Enable mismatch for {name}: expected 0, got {dut.control_unit.o_Mem_Write_Enable.value}"
        assert dut.control_unit.o_Pc_Alu_Mux_Select.value == 1, f"PC ALU Mux Select mismatch for {name}: expected 1, got {dut.control_unit.o_Pc_Alu_Mux_Select.value}"
        dut._log.info(f"{name} instruction test passed") 

@cocotb.test()
async def test_i_type_load_instructions(dut):
    tests = [
        ("LB", FUNC3_LOAD_LB, LS_TYPE_LOAD_BYTE),
        ("LH", FUNC3_LOAD_LH, LS_TYPE_LOAD_HALF),
        ("LW", FUNC3_LOAD_LW, LS_TYPE_LOAD_WORD),
        ("LBU", FUNC3_LOAD_LBU, LS_TYPE_LOAD_BYTE_UNSIGNED),
        ("LHU", FUNC3_LOAD_LHU, LS_TYPE_LOAD_HALF_UNSIGNED),
    ]

    for name, funct3, expected_ls in tests:
        dut._log.info(f"Starting {name} instruction test")

        dut.control_unit.i_Op_Code.value = OP_I_TYPE_LOAD
        dut.control_unit.i_Funct3.value = funct3
        dut.control_unit.i_Funct7_Bit_5.value = 0
        dut.control_unit.i_Branch_Enable.value = 0
        await Timer(wait_ns, units='ns')

        assert dut.control_unit.o_Port_A_Select.value == 1, f"Port A Select mismatch for {name}: expected 1, got {dut.control_unit.o_Port_A_Select.value}"
        assert dut.control_unit.o_Port_B_Select.value == 0, f"Port B Select mismatch for {name}: expected 0, got {dut.control_unit.o_Port_B_Select.value}"  
        assert dut.control_unit.o_Alu_Select.value == ALU_SEL_ADD, f"ALU Select mismatch for {name}: expected {ALU_SEL_ADD}, got {dut.control_unit.o_Alu_Select.value}"
        assert dut.control_unit.o_Cmp_Select.value == CMP_SEL_UNKNOWN, f"Comparator Select mismatch for {name}: expected {CMP_SEL_UNKNOWN}, got {dut.control_unit.o_Cmp_Select.value}"
        assert dut.control_unit.o_Imm_Select.value == IMM_I_TYPE, f"Immediate Select mismatch for {name}: expected {IMM_I_TYPE}, got {dut.control_unit.o_Imm_Select.value}"
        assert dut.control_unit.o_Load_Store_Type.value == expected_ls, f"Load/Store Type mismatch for {name}: expected {expected_ls}, got {dut.control_unit.o_Load_Store_Type.value}"
        assert dut.control_unit.o_Reg_Write_Select.value == REG_WRITE_DMEM, f"Reg Write Select mismatch for {name}: expected {REG_WRITE_DMEM}, got {dut.control_unit.o_Reg_Write_Select.value}"
        assert dut.control_unit.o_Reg_Write_Enable.value == 1, f"Reg Write Enable mismatch for {name}: expected 1, got {dut.control_unit.o_Reg_Write_Enable.value}"
        assert dut.control_unit.o_Mem_Write_Enable.value == 0, f"Mem Write Enable mismatch for {name}: expected 0, got {dut.control_unit.o_Mem_Write_Enable.value}"
        assert dut.control_unit.o_Pc_Alu_Mux_Select.value == 0, f"PC ALU Mux Select mismatch for {name}: expected 0, got {dut.control_unit.o_Pc_Alu_Mux_Select.value}"
        dut._log.info(f"{name} instruction test passed")


@cocotb.test()
async def test_s_type_instructions(dut):
    tests = [
        ("SB", 0b000, LS_TYPE_STORE_BYTE),
        ("SH", 0b001, LS_TYPE_STORE_HALF),
        ("SW", 0b010, LS_TYPE_STORE_WORD),
    ]

    for name, funct3, expected_ls in tests:
        dut._log.info(f"Starting {name} instruction test")

        dut.control_unit.i_Op_Code.value = OP_S_TYPE
        dut.control_unit.i_Funct3.value = funct3
        dut.control_unit.i_Funct7_Bit_5.value = 0
        dut.control_unit.i_Branch_Enable.value = 0
        await Timer(wait_ns, units='ns')

        assert dut.control_unit.o_Port_A_Select.value == 1, f"Port A Select mismatch for {name}: expected 1, got {dut.control_unit.o_Port_A_Select.value}"
        assert dut.control_unit.o_Port_B_Select.value == 0, f"Port B Select mismatch for {name}: expected 0, got {dut.control_unit.o_Port_B_Select.value}"  
        assert dut.control_unit.o_Alu_Select.value == ALU_SEL_ADD, f"ALU Select mismatch for {name}: expected {ALU_SEL_ADD}, got {dut.control_unit.o_Alu_Select.value}"
        assert dut.control_unit.o_Cmp_Select.value == CMP_SEL_UNKNOWN, f"Comparator Select mismatch for {name}: expected {CMP_SEL_UNKNOWN}, got {dut.control_unit.o_Cmp_Select.value}"
        assert dut.control_unit.o_Imm_Select.value == IMM_S_TYPE, f"Immediate Select mismatch for {name}: expected {IMM_S_TYPE}, got {dut.control_unit.o_Imm_Select.value}"
        assert dut.control_unit.o_Load_Store_Type.value == expected_ls, f"Load/Store Type mismatch for {name}: expected {expected_ls}, got {dut.control_unit.o_Load_Store_Type.value}"
        assert dut.control_unit.o_Reg_Write_Select.value == REG_WRITE_NONE, f"Reg Write Select mismatch for {name}: expected {REG_WRITE_NONE}, got {dut.control_unit.o_Reg_Write_Select.value}"
        assert dut.control_unit.o_Reg_Write_Enable.value == 0, f"Reg Write Enable mismatch for {name}: expected 0, got {dut.control_unit.o_Reg_Write_Enable.value}"
        assert dut.control_unit.o_Mem_Write_Enable.value == 1, f"Mem Write Enable mismatch for {name}: expected 1, got {dut.control_unit.o_Mem_Write_Enable.value}"
        assert dut.control_unit.o_Pc_Alu_Mux_Select.value == 0, f"PC ALU Mux Select mismatch for {name}: expected 0, got {dut.control_unit.o_Pc_Alu_Mux_Select.value}"
        dut._log.info(f"{name} instruction test passed")

@cocotb.test()
async def test_lui_instruction(dut):
    dut._log.info("Starting LUI instruction test")

    dut.control_unit.i_Op_Code.value = OP_U_TYPE_LUI
    dut.control_unit.i_Funct3.value = 0
    dut.control_unit.i_Funct7_Bit_5.value = 0
    dut.control_unit.i_Branch_Enable.value = 0
    await Timer(wait_ns, units='ns')

    assert dut.control_unit.o_Alu_Select.value == ALU_SEL_UNKNOWN, f"ALU Select mismatch: expected {ALU_SEL_ADD}, got {dut.control_unit.o_Alu_Select.value}"
    assert dut.control_unit.o_Cmp_Select.value == CMP_SEL_UNKNOWN, f"Comparator Select mismatch: expected {CMP_SEL_UNKNOWN}, got {dut.control_unit.o_Cmp_Select.value}"
    assert dut.control_unit.o_Imm_Select.value == IMM_U_TYPE, f"Immediate Select mismatch: expected {IMM_U_TYPE}, got {dut.control_unit.o_Imm_Select.value}"
    assert dut.control_unit.o_Load_Store_Type.value == LS_TYPE_NONE, f"Load/Store Type mismatch: expected {LS_TYPE_NONE}, got {dut.control_unit.o_Load_Store_Type.value}"
    assert dut.control_unit.o_Reg_Write_Select.value == REG_WRITE_IMM, f"Reg Write Select mismatch: expected {REG_WRITE_IMM}, got {dut.control_unit.o_Reg_Write_Select.value}"
    assert dut.control_unit.o_Reg_Write_Enable.value == 1, f"Reg Write Enable mismatch: expected 1, got {dut.control_unit.o_Reg_Write_Enable.value}"
    assert dut.control_unit.o_Mem_Write_Enable.value == 0, f"Mem Write Enable mismatch: expected 0, got {dut.control_unit.o_Mem_Write_Enable.value}"
    assert dut.control_unit.o_Pc_Alu_Mux_Select.value == 0, f"PC ALU Mux Select mismatch: expected 0, got {dut.control_unit.o_Pc_Alu_Mux_Select.value}"
    dut._log.info("LUI instruction test passed")

@cocotb.test()
async def test_auipc_instruction(dut):
    dut._log.info("Starting AUIPC instruction test")

    dut.control_unit.i_Op_Code.value = OP_U_TYPE_AUIPC
    dut.control_unit.i_Funct3.value = 0
    dut.control_unit.i_Funct7_Bit_5.value = 0
    dut.control_unit.i_Branch_Enable.value = 0
    await Timer(wait_ns, units='ns')

    assert dut.control_unit.o_Port_A_Select.value == 0, f"Port A Select mismatch: expected 0, got {dut.control_unit.o_Port_A_Select.value}"
    assert dut.control_unit.o_Port_B_Select.value == 0, f"Port B Select mismatch: expected 0, got {dut.control_unit.o_Port_B_Select.value}"  
    assert dut.control_unit.o_Alu_Select.value == ALU_SEL_ADD, f"ALU Select mismatch: expected {ALU_SEL_ADD}, got {dut.control_unit.o_Alu_Select.value}"
    assert dut.control_unit.o_Cmp_Select.value == CMP_SEL_UNKNOWN, f"Comparator Select mismatch: expected {CMP_SEL_UNKNOWN}, got {dut.control_unit.o_Cmp_Select.value}"
    assert dut.control_unit.o_Imm_Select.value == IMM_U_TYPE, f"Immediate Select mismatch: expected {IMM_U_TYPE}, got {dut.control_unit.o_Imm_Select.value}"
    assert dut.control_unit.o_Load_Store_Type.value == LS_TYPE_NONE, f"Load/Store Type mismatch: expected {LS_TYPE_NONE}, got {dut.control_unit.o_Load_Store_Type.value}"
    assert dut.control_unit.o_Reg_Write_Select.value == REG_WRITE_ALU, f"Reg Write Select mismatch: expected {REG_WRITE_IMM}, got {dut.control_unit.o_Reg_Write_Select.value}"
    assert dut.control_unit.o_Reg_Write_Enable.value == 1, f"Reg Write Enable mismatch: expected 1, got {dut.control_unit.o_Reg_Write_Enable.value}"
    assert dut.control_unit.o_Mem_Write_Enable.value == 0, f"Mem Write Enable mismatch: expected 0, got {dut.control_unit.o_Mem_Write_Enable.value}"
    assert dut.control_unit.o_Pc_Alu_Mux_Select.value == 0, f"PC ALU Mux Select mismatch: expected 0, got {dut.control_unit.o_Pc_Alu_Mux_Select.value}"
    dut._log.info("AUIPC instruction test passed")

@cocotb.test()
async def test_jal_instruction(dut):
    dut._log.info("Starting JAL instruction test")

    dut.control_unit.i_Op_Code.value = OP_J_TYPE
    dut.control_unit.i_Funct3.value = 0
    dut.control_unit.i_Funct7_Bit_5.value = 0
    dut.control_unit.i_Branch_Enable.value = 0
    await Timer(wait_ns, units='ns')

    assert dut.control_unit.o_Port_A_Select.value == 0, f"Port A Select mismatch: expected 0, got {dut.control_unit.o_Port_A_Select.value}"
    assert dut.control_unit.o_Port_B_Select.value == 0, f"Port B Select mismatch: expected 0, got {dut.control_unit.o_Port_B_Select.value}"  
    assert dut.control_unit.o_Alu_Select.value == ALU_SEL_ADD, f"ALU Select mismatch: expected {ALU_SEL_ADD}, got {dut.control_unit.o_Alu_Select.value}"
    assert dut.control_unit.o_Cmp_Select.value == CMP_SEL_UNKNOWN, f"Comparator Select mismatch: expected {CMP_SEL_UNKNOWN}, got {dut.control_unit.o_Cmp_Select.value}"
    assert dut.control_unit.o_Imm_Select.value == IMM_J_TYPE, f"Immediate Select mismatch: expected {IMM_J_TYPE}, got {dut.control_unit.o_Imm_Select.value}"
    assert dut.control_unit.o_Load_Store_Type.value == LS_TYPE_NONE, f"Load/Store Type mismatch: expected {LS_TYPE_NONE}, got {dut.control_unit.o_Load_Store_Type.value}"
    assert dut.control_unit.o_Reg_Write_Select.value == REG_WRITE_PC_NEXT, f"Reg Write Select mismatch: expected {REG_WRITE_PC_NEXT}, got {dut.control_unit.o_Reg_Write_Select.value}"
    assert dut.control_unit.o_Reg_Write_Enable.value == 1, f"Reg Write Enable mismatch: expected 1, got {dut.control_unit.o_Reg_Write_Enable.value}"
    assert dut.control_unit.o_Mem_Write_Enable.value == 0, f"Mem Write Enable mismatch: expected 0, got {dut.control_unit.o_Mem_Write_Enable.value}"
    assert dut.control_unit.o_Pc_Alu_Mux_Select.value == 1, f"PC ALU Mux Select mismatch: expected 1, got {dut.control_unit.o_Pc_Alu_Mux_Select.value}"
    dut._log.info("JAL instruction test passed")

@cocotb.test()
async def test_jalr_instruction(dut):
    dut._log.info("Starting JALR instruction test")

    dut.control_unit.i_Op_Code.value = OP_I_TYPE_JALR
    dut.control_unit.i_Funct3.value = 0
    dut.control_unit.i_Funct7_Bit_5.value = 0
    dut.control_unit.i_Branch_Enable.value = 0
    await Timer(wait_ns, units='ns')

    assert dut.control_unit.o_Port_A_Select.value == 1, f"Port A Select mismatch: expected 1, got {dut.control_unit.o_Port_A_Select.value}"
    assert dut.control_unit.o_Port_B_Select.value == 0, f"Port B Select mismatch: expected 0, got {dut.control_unit.o_Port_B_Select.value}"  
    assert dut.control_unit.o_Alu_Select.value == ALU_SEL_ADD, f"ALU Select mismatch: expected {ALU_SEL_ADD}, got {dut.control_unit.o_Alu_Select.value}"
    assert dut.control_unit.o_Cmp_Select.value == CMP_SEL_UNKNOWN, f"Comparator Select mismatch: expected {CMP_SEL_UNKNOWN}, got {dut.control_unit.o_Cmp_Select.value}"
    assert dut.control_unit.o_Imm_Select.value == IMM_I_TYPE, f"Immediate Select mismatch: expected {IMM_I_TYPE}, got {dut.control_unit.o_Imm_Select.value}"
    assert dut.control_unit.o_Load_Store_Type.value == LS_TYPE_NONE, f"Load/Store Type mismatch: expected {LS_TYPE_NONE}, got {dut.control_unit.o_Load_Store_Type.value}"
    assert dut.control_unit.o_Reg_Write_Select.value == REG_WRITE_PC_NEXT, f"Reg Write Select mismatch: expected {REG_WRITE_PC_NEXT}, got {dut.control_unit.o_Reg_Write_Select.value}"
    assert dut.control_unit.o_Reg_Write_Enable.value == 1, f"Reg Write Enable mismatch: expected 1, got {dut.control_unit.o_Reg_Write_Enable.value}"
    assert dut.control_unit.o_Mem_Write_Enable.value == 0, f"Mem Write Enable mismatch: expected 0, got {dut.control_unit.o_Mem_Write_Enable.value}"
    assert dut.control_unit.o_Pc_Alu_Mux_Select.value == 1, f"PC ALU Mux Select mismatch: expected 1, got {dut.control_unit.o_Pc_Alu_Mux_Select.value}"
    dut._log.info("JALR instruction test passed")

@cocotb.test()
async def test_unknown_instruction(dut):
    dut._log.info("Starting unknown instruction test")

    dut.control_unit.i_Op_Code.value = 0b0000000  # Invalid opcode
    dut.control_unit.i_Funct3.value = 0
    dut.control_unit.i_Funct7_Bit_5.value = 0
    dut.control_unit.i_Branch_Enable.value = 0
    await Timer(wait_ns, units='ns')
    assert dut.control_unit.o_Port_A_Select.value == 0, f"Port A Select mismatch: expected 0, got {dut.control_unit.o_Port_A_Select.value}"
    assert dut.control_unit.o_Port_B_Select.value == 0, f"Port B Select mismatch: expected 0, got {dut.control_unit.o_Port_B_Select.value}"  
    assert dut.control_unit.o_Alu_Select.value == ALU_SEL_UNKNOWN, f"ALU Select mismatch: expected {ALU_SEL_UNKNOWN}, got {dut.control_unit.o_Alu_Select.value}"
    assert dut.control_unit.o_Cmp_Select.value == CMP_SEL_UNKNOWN, f"Comparator Select mismatch: expected {CMP_SEL_UNKNOWN}, got {dut.control_unit.o_Cmp_Select.value}"
    assert dut.control_unit.o_Imm_Select.value == IMM_UNKNOWN_TYPE, f"Immediate Select mismatch: expected {IMM_UNKNOWN_TYPE}, got {dut.control_unit.o_Imm_Select.value}"
    assert dut.control_unit.o_Load_Store_Type.value == LS_TYPE_NONE, f"Load/Store Type mismatch: expected {LS_TYPE_NONE}, got {dut.control_unit.o_Load_Store_Type.value}"
    assert dut.control_unit.o_Reg_Write_Select.value == REG_WRITE_NONE, f"Reg Write Select mismatch: expected {REG_WRITE_NONE}, got {dut.control_unit.o_Reg_Write_Select.value}"
    assert dut.control_unit.o_Reg_Write_Enable.value == 0, f"Reg Write Enable mismatch: expected 0, got {dut.control_unit.o_Reg_Write_Enable.value}"
    assert dut.control_unit.o_Mem_Write_Enable.value == 0, f"Mem Write Enable mismatch: expected 0, got {dut.control_unit.o_Mem_Write_Enable.value}"
    assert dut.control_unit.o_Pc_Alu_Mux_Select.value == 0, f"PC ALU Mux Select mismatch: expected 0, got {dut.control_unit.o_Pc_Alu_Mux_Select.value}"
    dut._log.info("Unknown instruction test passed")