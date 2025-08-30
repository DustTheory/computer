// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vtop.h for the primary calling header

#ifndef VERILATED_VTOP___024ROOT_H_
#define VERILATED_VTOP___024ROOT_H_  // guard

#include "verilated.h"
class Vtop___024unit;


class Vtop__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vtop___024root final : public VerilatedModule {
  public:
    // CELLS
    Vtop___024unit* __PVT____024unit;

    // DESIGN SPECIFIC STATE
    CData/*4:0*/ harness__DOT__alu__DOT__i_Alu_Select;
    CData/*3:0*/ harness__DOT__comparator_unit__DOT__i_Compare_Select;
    CData/*0:0*/ harness__DOT__comparator_unit__DOT__o_Compare_Result;
    CData/*3:0*/ harness__DOT__immediate_unit__DOT__i_Imm_Select;
    CData/*0:0*/ __VstlFirstIteration;
    CData/*0:0*/ __VicoFirstIteration;
    CData/*0:0*/ __VactContinue;
    IData/*31:0*/ harness__DOT__alu__DOT__i_Input_A;
    IData/*31:0*/ harness__DOT__alu__DOT__i_Input_B;
    IData/*31:0*/ harness__DOT__alu__DOT__o_Alu_Result;
    IData/*31:0*/ harness__DOT__comparator_unit__DOT__i_Input_A;
    IData/*31:0*/ harness__DOT__comparator_unit__DOT__i_Input_B;
    IData/*24:0*/ harness__DOT__immediate_unit__DOT__i_Instruction_No_Opcode;
    IData/*31:0*/ harness__DOT__immediate_unit__DOT__o_Immediate;
    IData/*31:0*/ __VactIterCount;
    VlTriggerVec<1> __VstlTriggered;
    VlTriggerVec<1> __VicoTriggered;
    VlTriggerVec<0> __VactTriggered;
    VlTriggerVec<0> __VnbaTriggered;

    // INTERNAL VARIABLES
    Vtop__Syms* const vlSymsp;

    // PARAMETERS
    static constexpr IData/*31:0*/ harness__DOT__XLEN = 0x00000020U;
    static constexpr IData/*31:0*/ harness__DOT__REG_ADDR_WIDTH = 5U;

    // CONSTRUCTORS
    Vtop___024root(Vtop__Syms* symsp, const char* v__name);
    ~Vtop___024root();
    VL_UNCOPYABLE(Vtop___024root);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
