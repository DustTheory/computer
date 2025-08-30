// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table implementation internals

#include "Vtop__pch.h"
#include "Vtop.h"
#include "Vtop___024root.h"
#include "Vtop___024unit.h"

// FUNCTIONS
Vtop__Syms::~Vtop__Syms()
{

    // Tear down scope hierarchy
    __Vhier.remove(0, &__Vscope___024unit);
    __Vhier.remove(0, &__Vscope_harness);
    __Vhier.remove(&__Vscope_harness, &__Vscope_harness__alu);
    __Vhier.remove(&__Vscope_harness, &__Vscope_harness__comparator_unit);
    __Vhier.remove(&__Vscope_harness, &__Vscope_harness__immediate_unit);

}

Vtop__Syms::Vtop__Syms(VerilatedContext* contextp, const char* namep, Vtop* modelp)
    : VerilatedSyms{contextp}
    // Setup internal state of the Syms class
    , __Vm_modelp{modelp}
    // Setup module instances
    , TOP{this, namep}
    , TOP____024unit{this, Verilated::catName(namep, "$unit")}
{
        // Check resources
        Verilated::stackCheck(25);
    // Configure time unit / time precision
    _vm_contextp__->timeunit(-9);
    _vm_contextp__->timeprecision(-12);
    // Setup each module's pointers to their submodules
    TOP.__PVT____024unit = &TOP____024unit;
    // Setup each module's pointer back to symbol table (for public functions)
    TOP.__Vconfigure(true);
    TOP____024unit.__Vconfigure(true);
    // Setup scopes
    __Vscope___024unit.configure(this, name(), "\\$unit ", "\\$unit ", "__024unit", -9, VerilatedScope::SCOPE_PACKAGE);
    __Vscope_harness.configure(this, name(), "harness", "harness", "harness", -9, VerilatedScope::SCOPE_MODULE);
    __Vscope_harness__alu.configure(this, name(), "harness.alu", "alu", "arithmetic_logic_unit", -9, VerilatedScope::SCOPE_MODULE);
    __Vscope_harness__comparator_unit.configure(this, name(), "harness.comparator_unit", "comparator_unit", "comparator_unit", -9, VerilatedScope::SCOPE_MODULE);
    __Vscope_harness__immediate_unit.configure(this, name(), "harness.immediate_unit", "immediate_unit", "immediate_unit", -9, VerilatedScope::SCOPE_MODULE);

    // Set up scope hierarchy
    __Vhier.add(0, &__Vscope___024unit);
    __Vhier.add(0, &__Vscope_harness);
    __Vhier.add(&__Vscope_harness, &__Vscope_harness__alu);
    __Vhier.add(&__Vscope_harness, &__Vscope_harness__comparator_unit);
    __Vhier.add(&__Vscope_harness, &__Vscope_harness__immediate_unit);

    // Setup export functions
    for (int __Vfinal = 0; __Vfinal < 2; ++__Vfinal) {
        __Vscope___024unit.varInsert(__Vfinal,"ALU_SEL_ADD", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.ALU_SEL_ADD))), true, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,4,0);
        __Vscope___024unit.varInsert(__Vfinal,"ALU_SEL_AND", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.ALU_SEL_AND))), true, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,4,0);
        __Vscope___024unit.varInsert(__Vfinal,"ALU_SEL_OR", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.ALU_SEL_OR))), true, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,4,0);
        __Vscope___024unit.varInsert(__Vfinal,"ALU_SEL_SLL", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.ALU_SEL_SLL))), true, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,4,0);
        __Vscope___024unit.varInsert(__Vfinal,"ALU_SEL_SRA", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.ALU_SEL_SRA))), true, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,4,0);
        __Vscope___024unit.varInsert(__Vfinal,"ALU_SEL_SRL", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.ALU_SEL_SRL))), true, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,4,0);
        __Vscope___024unit.varInsert(__Vfinal,"ALU_SEL_SUB", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.ALU_SEL_SUB))), true, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,4,0);
        __Vscope___024unit.varInsert(__Vfinal,"ALU_SEL_UNKNOWN", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.ALU_SEL_UNKNOWN))), true, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,4,0);
        __Vscope___024unit.varInsert(__Vfinal,"ALU_SEL_WIDTH", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.ALU_SEL_WIDTH))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope___024unit.varInsert(__Vfinal,"ALU_SEL_XOR", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.ALU_SEL_XOR))), true, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,4,0);
        __Vscope___024unit.varInsert(__Vfinal,"CMP_SEL_BEQ", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.CMP_SEL_BEQ))), true, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope___024unit.varInsert(__Vfinal,"CMP_SEL_BGE", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.CMP_SEL_BGE))), true, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope___024unit.varInsert(__Vfinal,"CMP_SEL_BGEU", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.CMP_SEL_BGEU))), true, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope___024unit.varInsert(__Vfinal,"CMP_SEL_BLT", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.CMP_SEL_BLT))), true, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope___024unit.varInsert(__Vfinal,"CMP_SEL_BLTU", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.CMP_SEL_BLTU))), true, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope___024unit.varInsert(__Vfinal,"CMP_SEL_BNE", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.CMP_SEL_BNE))), true, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope___024unit.varInsert(__Vfinal,"CMP_SEL_UNKNOWN", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.CMP_SEL_UNKNOWN))), true, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope___024unit.varInsert(__Vfinal,"CMP_SEL_WIDTH", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.CMP_SEL_WIDTH))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope___024unit.varInsert(__Vfinal,"IMM_B_TYPE", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.IMM_B_TYPE))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope___024unit.varInsert(__Vfinal,"IMM_I_TYPE", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.IMM_I_TYPE))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope___024unit.varInsert(__Vfinal,"IMM_J_TYPE", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.IMM_J_TYPE))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope___024unit.varInsert(__Vfinal,"IMM_SEL_WIDTH", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.IMM_SEL_WIDTH))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope___024unit.varInsert(__Vfinal,"IMM_S_TYPE", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.IMM_S_TYPE))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope___024unit.varInsert(__Vfinal,"IMM_UNKNOWN_TYPE", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.IMM_UNKNOWN_TYPE))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope___024unit.varInsert(__Vfinal,"IMM_U_TYPE", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.IMM_U_TYPE))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope___024unit.varInsert(__Vfinal,"REG_ADDR_WIDTH", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.REG_ADDR_WIDTH))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope___024unit.varInsert(__Vfinal,"REG_WRITE_ALU", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.REG_WRITE_ALU))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope___024unit.varInsert(__Vfinal,"REG_WRITE_CU", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.REG_WRITE_CU))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope___024unit.varInsert(__Vfinal,"REG_WRITE_DMEM", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.REG_WRITE_DMEM))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope___024unit.varInsert(__Vfinal,"REG_WRITE_IMM", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.REG_WRITE_IMM))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope___024unit.varInsert(__Vfinal,"REG_WRITE_NONE", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.REG_WRITE_NONE))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope___024unit.varInsert(__Vfinal,"REG_WRITE_PC_NEXT", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.REG_WRITE_PC_NEXT))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope___024unit.varInsert(__Vfinal,"XLEN", const_cast<void*>(static_cast<const void*>(&(TOP____024unit.XLEN))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_harness.varInsert(__Vfinal,"REG_ADDR_WIDTH", const_cast<void*>(static_cast<const void*>(&(TOP.harness__DOT__REG_ADDR_WIDTH))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_harness.varInsert(__Vfinal,"XLEN", const_cast<void*>(static_cast<const void*>(&(TOP.harness__DOT__XLEN))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_harness__alu.varInsert(__Vfinal,"i_Alu_Select", &(TOP.harness__DOT__alu__DOT__i_Alu_Select), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,4,0);
        __Vscope_harness__alu.varInsert(__Vfinal,"i_Input_A", &(TOP.harness__DOT__alu__DOT__i_Input_A), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_harness__alu.varInsert(__Vfinal,"i_Input_B", &(TOP.harness__DOT__alu__DOT__i_Input_B), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_harness__alu.varInsert(__Vfinal,"o_Alu_Result", &(TOP.harness__DOT__alu__DOT__o_Alu_Result), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_harness__comparator_unit.varInsert(__Vfinal,"i_Compare_Select", &(TOP.harness__DOT__comparator_unit__DOT__i_Compare_Select), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope_harness__comparator_unit.varInsert(__Vfinal,"i_Input_A", &(TOP.harness__DOT__comparator_unit__DOT__i_Input_A), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_harness__comparator_unit.varInsert(__Vfinal,"i_Input_B", &(TOP.harness__DOT__comparator_unit__DOT__i_Input_B), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_harness__comparator_unit.varInsert(__Vfinal,"o_Compare_Result", &(TOP.harness__DOT__comparator_unit__DOT__o_Compare_Result), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_harness__immediate_unit.varInsert(__Vfinal,"i_Imm_Select", &(TOP.harness__DOT__immediate_unit__DOT__i_Imm_Select), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope_harness__immediate_unit.varInsert(__Vfinal,"i_Instruction_No_Opcode", &(TOP.harness__DOT__immediate_unit__DOT__i_Instruction_No_Opcode), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,7);
        __Vscope_harness__immediate_unit.varInsert(__Vfinal,"o_Immediate", &(TOP.harness__DOT__immediate_unit__DOT__o_Immediate), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
    }
}
