// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtop.h for the primary calling header

#include "Vtop__pch.h"
#include "Vtop__Syms.h"
#include "Vtop___024unit.h"

// Parameter definitions for Vtop___024unit
constexpr CData/*3:0*/ Vtop___024unit::CMP_SEL_BEQ;
constexpr CData/*3:0*/ Vtop___024unit::CMP_SEL_BNE;
constexpr CData/*3:0*/ Vtop___024unit::CMP_SEL_BLTU;
constexpr CData/*3:0*/ Vtop___024unit::CMP_SEL_BGEU;
constexpr CData/*3:0*/ Vtop___024unit::CMP_SEL_BLT;
constexpr CData/*3:0*/ Vtop___024unit::CMP_SEL_BGE;
constexpr CData/*3:0*/ Vtop___024unit::CMP_SEL_UNKNOWN;
constexpr CData/*4:0*/ Vtop___024unit::ALU_SEL_ADD;
constexpr CData/*4:0*/ Vtop___024unit::ALU_SEL_SUB;
constexpr CData/*4:0*/ Vtop___024unit::ALU_SEL_AND;
constexpr CData/*4:0*/ Vtop___024unit::ALU_SEL_OR;
constexpr CData/*4:0*/ Vtop___024unit::ALU_SEL_XOR;
constexpr CData/*4:0*/ Vtop___024unit::ALU_SEL_SLL;
constexpr CData/*4:0*/ Vtop___024unit::ALU_SEL_SRL;
constexpr CData/*4:0*/ Vtop___024unit::ALU_SEL_SRA;
constexpr CData/*4:0*/ Vtop___024unit::ALU_SEL_UNKNOWN;
constexpr IData/*31:0*/ Vtop___024unit::XLEN;
constexpr IData/*31:0*/ Vtop___024unit::REG_ADDR_WIDTH;
constexpr IData/*31:0*/ Vtop___024unit::ALU_SEL_WIDTH;
constexpr IData/*31:0*/ Vtop___024unit::CMP_SEL_WIDTH;
constexpr IData/*31:0*/ Vtop___024unit::IMM_SEL_WIDTH;
constexpr IData/*31:0*/ Vtop___024unit::REG_WRITE_ALU;
constexpr IData/*31:0*/ Vtop___024unit::REG_WRITE_CU;
constexpr IData/*31:0*/ Vtop___024unit::REG_WRITE_IMM;
constexpr IData/*31:0*/ Vtop___024unit::REG_WRITE_PC_NEXT;
constexpr IData/*31:0*/ Vtop___024unit::REG_WRITE_DMEM;
constexpr IData/*31:0*/ Vtop___024unit::REG_WRITE_NONE;
constexpr IData/*31:0*/ Vtop___024unit::IMM_U_TYPE;
constexpr IData/*31:0*/ Vtop___024unit::IMM_B_TYPE;
constexpr IData/*31:0*/ Vtop___024unit::IMM_I_TYPE;
constexpr IData/*31:0*/ Vtop___024unit::IMM_J_TYPE;
constexpr IData/*31:0*/ Vtop___024unit::IMM_S_TYPE;
constexpr IData/*31:0*/ Vtop___024unit::IMM_UNKNOWN_TYPE;


void Vtop___024unit___ctor_var_reset(Vtop___024unit* vlSelf);

Vtop___024unit::Vtop___024unit(Vtop__Syms* symsp, const char* v__name)
    : VerilatedModule{v__name}
    , vlSymsp{symsp}
 {
    // Reset structure values
    Vtop___024unit___ctor_var_reset(this);
}

void Vtop___024unit::__Vconfigure(bool first) {
    (void)first;  // Prevent unused variable warning
}

Vtop___024unit::~Vtop___024unit() {
}
