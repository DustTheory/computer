def gen_i_type_instruction(opcode, rd, funct3, rs1, imm):
    instruction = opcode
    instruction |= rd << 7
    instruction |= funct3 << 12
    instruction |= rs1 << 15
    instruction |= (imm & 0b111111111111) << 20
    return instruction