// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vtop.h for the primary calling header

#ifndef VERILATED_VTOP___024UNIT_H_
#define VERILATED_VTOP___024UNIT_H_  // guard

#include "verilated.h"


class Vtop__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vtop___024unit final : public VerilatedModule {
  public:

    // INTERNAL VARIABLES
    Vtop__Syms* const vlSymsp;

    // PARAMETERS
    static constexpr CData/*3:0*/ CMP_SEL_BEQ = 0U;
    static constexpr CData/*3:0*/ CMP_SEL_BNE = 1U;
    static constexpr CData/*3:0*/ CMP_SEL_BLTU = 2U;
    static constexpr CData/*3:0*/ CMP_SEL_BGEU = 3U;
    static constexpr CData/*3:0*/ CMP_SEL_BLT = 4U;
    static constexpr CData/*3:0*/ CMP_SEL_BGE = 5U;
    static constexpr CData/*3:0*/ CMP_SEL_UNKNOWN = 6U;
    static constexpr CData/*4:0*/ ALU_SEL_ADD = 0U;
    static constexpr CData/*4:0*/ ALU_SEL_SUB = 1U;
    static constexpr CData/*4:0*/ ALU_SEL_AND = 2U;
    static constexpr CData/*4:0*/ ALU_SEL_OR = 3U;
    static constexpr CData/*4:0*/ ALU_SEL_XOR = 4U;
    static constexpr CData/*4:0*/ ALU_SEL_SLL = 5U;
    static constexpr CData/*4:0*/ ALU_SEL_SRL = 6U;
    static constexpr CData/*4:0*/ ALU_SEL_SRA = 7U;
    static constexpr CData/*4:0*/ ALU_SEL_UNKNOWN = 8U;
    static constexpr IData/*31:0*/ XLEN = 0x00000020U;
    static constexpr IData/*31:0*/ REG_ADDR_WIDTH = 5U;
    static constexpr IData/*31:0*/ ALU_SEL_WIDTH = 4U;
    static constexpr IData/*31:0*/ CMP_SEL_WIDTH = 3U;
    static constexpr IData/*31:0*/ IMM_SEL_WIDTH = 3U;
    static constexpr IData/*31:0*/ REG_WRITE_ALU = 0U;
    static constexpr IData/*31:0*/ REG_WRITE_CU = 1U;
    static constexpr IData/*31:0*/ REG_WRITE_IMM = 2U;
    static constexpr IData/*31:0*/ REG_WRITE_PC_NEXT = 3U;
    static constexpr IData/*31:0*/ REG_WRITE_DMEM = 4U;
    static constexpr IData/*31:0*/ REG_WRITE_NONE = 5U;
    static constexpr IData/*31:0*/ IMM_U_TYPE = 0U;
    static constexpr IData/*31:0*/ IMM_B_TYPE = 1U;
    static constexpr IData/*31:0*/ IMM_I_TYPE = 2U;
    static constexpr IData/*31:0*/ IMM_J_TYPE = 3U;
    static constexpr IData/*31:0*/ IMM_S_TYPE = 4U;
    static constexpr IData/*31:0*/ IMM_UNKNOWN_TYPE = 5U;

    // CONSTRUCTORS
    Vtop___024unit(Vtop__Syms* symsp, const char* v__name);
    ~Vtop___024unit();
    VL_UNCOPYABLE(Vtop___024unit);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
