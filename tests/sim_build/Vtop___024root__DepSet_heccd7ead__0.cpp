// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtop.h for the primary calling header

#include "Vtop__pch.h"
#include "Vtop___024root.h"

void Vtop___024root___ico_sequent__TOP__0(Vtop___024root* vlSelf);

void Vtop___024root___eval_ico(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_ico\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VicoTriggered.word(0U))) {
        Vtop___024root___ico_sequent__TOP__0(vlSelf);
    }
}

VL_INLINE_OPT void Vtop___024root___ico_sequent__TOP__0(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___ico_sequent__TOP__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((0U == (IData)(vlSelfRef.harness__DOT__immediate_unit__DOT__i_Imm_Select))) {
        vlSelfRef.harness__DOT__immediate_unit__DOT__o_Immediate 
            = (0xfffff000U & (vlSelfRef.harness__DOT__immediate_unit__DOT__i_Instruction_No_Opcode 
                              << 7U));
    } else if ((3U == (IData)(vlSelfRef.harness__DOT__immediate_unit__DOT__i_Imm_Select))) {
        vlSelfRef.harness__DOT__immediate_unit__DOT__o_Immediate 
            = VL_EXTENDS_II(32,21, (((0x100000U & (vlSelfRef.harness__DOT__immediate_unit__DOT__i_Instruction_No_Opcode 
                                                   >> 4U)) 
                                     | ((0xff000U & 
                                         (vlSelfRef.harness__DOT__immediate_unit__DOT__i_Instruction_No_Opcode 
                                          << 7U)) | 
                                        (0x800U & (vlSelfRef.harness__DOT__immediate_unit__DOT__i_Instruction_No_Opcode 
                                                   >> 2U)))) 
                                    | (0x7feU & (vlSelfRef.harness__DOT__immediate_unit__DOT__i_Instruction_No_Opcode 
                                                 >> 0xdU))));
    } else if ((2U == (IData)(vlSelfRef.harness__DOT__immediate_unit__DOT__i_Imm_Select))) {
        vlSelfRef.harness__DOT__immediate_unit__DOT__o_Immediate 
            = VL_EXTENDS_II(32,12, (0xfffU & (vlSelfRef.harness__DOT__immediate_unit__DOT__i_Instruction_No_Opcode 
                                              >> 0xdU)));
    } else if ((4U == (IData)(vlSelfRef.harness__DOT__immediate_unit__DOT__i_Imm_Select))) {
        vlSelfRef.harness__DOT__immediate_unit__DOT__o_Immediate 
            = VL_EXTENDS_II(32,12, ((0xfe0U & (vlSelfRef.harness__DOT__immediate_unit__DOT__i_Instruction_No_Opcode 
                                               >> 0xdU)) 
                                    | (0x1fU & vlSelfRef.harness__DOT__immediate_unit__DOT__i_Instruction_No_Opcode)));
    } else if ((1U == (IData)(vlSelfRef.harness__DOT__immediate_unit__DOT__i_Imm_Select))) {
        vlSelfRef.harness__DOT__immediate_unit__DOT__o_Immediate 
            = VL_EXTENDS_II(32,13, (((0x1000U & (vlSelfRef.harness__DOT__immediate_unit__DOT__i_Instruction_No_Opcode 
                                                 >> 0xcU)) 
                                     | (0x800U & (vlSelfRef.harness__DOT__immediate_unit__DOT__i_Instruction_No_Opcode 
                                                  << 0xbU))) 
                                    | ((0x7e0U & (vlSelfRef.harness__DOT__immediate_unit__DOT__i_Instruction_No_Opcode 
                                                  >> 0xdU)) 
                                       | (0x1eU & vlSelfRef.harness__DOT__immediate_unit__DOT__i_Instruction_No_Opcode))));
    } else if ((5U == (IData)(vlSelfRef.harness__DOT__immediate_unit__DOT__i_Imm_Select))) {
        vlSelfRef.harness__DOT__immediate_unit__DOT__o_Immediate = 0U;
    }
    vlSelfRef.harness__DOT__alu__DOT__o_Alu_Result 
        = ((0x10U & (IData)(vlSelfRef.harness__DOT__alu__DOT__i_Alu_Select))
            ? 0U : ((8U & (IData)(vlSelfRef.harness__DOT__alu__DOT__i_Alu_Select))
                     ? 0U : ((4U & (IData)(vlSelfRef.harness__DOT__alu__DOT__i_Alu_Select))
                              ? ((2U & (IData)(vlSelfRef.harness__DOT__alu__DOT__i_Alu_Select))
                                  ? ((1U & (IData)(vlSelfRef.harness__DOT__alu__DOT__i_Alu_Select))
                                      ? VL_SHIFTRS_III(32,32,5, vlSelfRef.harness__DOT__alu__DOT__i_Input_A, 
                                                       (0x1fU 
                                                        & vlSelfRef.harness__DOT__alu__DOT__i_Input_B))
                                      : (vlSelfRef.harness__DOT__alu__DOT__i_Input_A 
                                         >> (0x1fU 
                                             & vlSelfRef.harness__DOT__alu__DOT__i_Input_B)))
                                  : ((1U & (IData)(vlSelfRef.harness__DOT__alu__DOT__i_Alu_Select))
                                      ? (vlSelfRef.harness__DOT__alu__DOT__i_Input_A 
                                         << (0x1fU 
                                             & vlSelfRef.harness__DOT__alu__DOT__i_Input_B))
                                      : (vlSelfRef.harness__DOT__alu__DOT__i_Input_A 
                                         ^ vlSelfRef.harness__DOT__alu__DOT__i_Input_B)))
                              : ((2U & (IData)(vlSelfRef.harness__DOT__alu__DOT__i_Alu_Select))
                                  ? ((1U & (IData)(vlSelfRef.harness__DOT__alu__DOT__i_Alu_Select))
                                      ? (vlSelfRef.harness__DOT__alu__DOT__i_Input_A 
                                         | vlSelfRef.harness__DOT__alu__DOT__i_Input_B)
                                      : (vlSelfRef.harness__DOT__alu__DOT__i_Input_A 
                                         & vlSelfRef.harness__DOT__alu__DOT__i_Input_B))
                                  : ((1U & (IData)(vlSelfRef.harness__DOT__alu__DOT__i_Alu_Select))
                                      ? (vlSelfRef.harness__DOT__alu__DOT__i_Input_A 
                                         - vlSelfRef.harness__DOT__alu__DOT__i_Input_B)
                                      : (vlSelfRef.harness__DOT__alu__DOT__i_Input_A 
                                         + vlSelfRef.harness__DOT__alu__DOT__i_Input_B))))));
    vlSelfRef.harness__DOT__comparator_unit__DOT__o_Compare_Result 
        = ((1U & (~ ((IData)(vlSelfRef.harness__DOT__comparator_unit__DOT__i_Compare_Select) 
                     >> 3U))) && ((4U & (IData)(vlSelfRef.harness__DOT__comparator_unit__DOT__i_Compare_Select))
                                   ? ((1U & (~ ((IData)(vlSelfRef.harness__DOT__comparator_unit__DOT__i_Compare_Select) 
                                                >> 1U))) 
                                      && ((1U & (IData)(vlSelfRef.harness__DOT__comparator_unit__DOT__i_Compare_Select))
                                           ? VL_GTES_III(32, vlSelfRef.harness__DOT__comparator_unit__DOT__i_Input_A, vlSelfRef.harness__DOT__comparator_unit__DOT__i_Input_B)
                                           : VL_LTS_III(32, vlSelfRef.harness__DOT__comparator_unit__DOT__i_Input_A, vlSelfRef.harness__DOT__comparator_unit__DOT__i_Input_B)))
                                   : ((2U & (IData)(vlSelfRef.harness__DOT__comparator_unit__DOT__i_Compare_Select))
                                       ? ((1U & (IData)(vlSelfRef.harness__DOT__comparator_unit__DOT__i_Compare_Select))
                                           ? (vlSelfRef.harness__DOT__comparator_unit__DOT__i_Input_A 
                                              >= vlSelfRef.harness__DOT__comparator_unit__DOT__i_Input_B)
                                           : (vlSelfRef.harness__DOT__comparator_unit__DOT__i_Input_A 
                                              < vlSelfRef.harness__DOT__comparator_unit__DOT__i_Input_B))
                                       : ((1U & (IData)(vlSelfRef.harness__DOT__comparator_unit__DOT__i_Compare_Select))
                                           ? (vlSelfRef.harness__DOT__comparator_unit__DOT__i_Input_A 
                                              != vlSelfRef.harness__DOT__comparator_unit__DOT__i_Input_B)
                                           : (vlSelfRef.harness__DOT__comparator_unit__DOT__i_Input_A 
                                              == vlSelfRef.harness__DOT__comparator_unit__DOT__i_Input_B)))));
}

void Vtop___024root___eval_triggers__ico(Vtop___024root* vlSelf);

bool Vtop___024root___eval_phase__ico(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_phase__ico\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    CData/*0:0*/ __VicoExecute;
    // Body
    Vtop___024root___eval_triggers__ico(vlSelf);
    __VicoExecute = vlSelfRef.__VicoTriggered.any();
    if (__VicoExecute) {
        Vtop___024root___eval_ico(vlSelf);
    }
    return (__VicoExecute);
}

void Vtop___024root___eval_act(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_act\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

void Vtop___024root___eval_nba(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_nba\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

void Vtop___024root___eval_triggers__act(Vtop___024root* vlSelf);

bool Vtop___024root___eval_phase__act(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_phase__act\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    VlTriggerVec<0> __VpreTriggered;
    CData/*0:0*/ __VactExecute;
    // Body
    Vtop___024root___eval_triggers__act(vlSelf);
    __VactExecute = vlSelfRef.__VactTriggered.any();
    if (__VactExecute) {
        __VpreTriggered.andNot(vlSelfRef.__VactTriggered, vlSelfRef.__VnbaTriggered);
        vlSelfRef.__VnbaTriggered.thisOr(vlSelfRef.__VactTriggered);
        Vtop___024root___eval_act(vlSelf);
    }
    return (__VactExecute);
}

bool Vtop___024root___eval_phase__nba(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_phase__nba\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    CData/*0:0*/ __VnbaExecute;
    // Body
    __VnbaExecute = vlSelfRef.__VnbaTriggered.any();
    if (__VnbaExecute) {
        Vtop___024root___eval_nba(vlSelf);
        vlSelfRef.__VnbaTriggered.clear();
    }
    return (__VnbaExecute);
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__ico(Vtop___024root* vlSelf);
#endif  // VL_DEBUG
#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__nba(Vtop___024root* vlSelf);
#endif  // VL_DEBUG
#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__act(Vtop___024root* vlSelf);
#endif  // VL_DEBUG

void Vtop___024root___eval(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    IData/*31:0*/ __VicoIterCount;
    CData/*0:0*/ __VicoContinue;
    IData/*31:0*/ __VnbaIterCount;
    CData/*0:0*/ __VnbaContinue;
    // Body
    __VicoIterCount = 0U;
    vlSelfRef.__VicoFirstIteration = 1U;
    __VicoContinue = 1U;
    while (__VicoContinue) {
        if (VL_UNLIKELY(((0x64U < __VicoIterCount)))) {
#ifdef VL_DEBUG
            Vtop___024root___dump_triggers__ico(vlSelf);
#endif
            VL_FATAL_MT("harness.v", 3, "", "Input combinational region did not converge.");
        }
        __VicoIterCount = ((IData)(1U) + __VicoIterCount);
        __VicoContinue = 0U;
        if (Vtop___024root___eval_phase__ico(vlSelf)) {
            __VicoContinue = 1U;
        }
        vlSelfRef.__VicoFirstIteration = 0U;
    }
    __VnbaIterCount = 0U;
    __VnbaContinue = 1U;
    while (__VnbaContinue) {
        if (VL_UNLIKELY(((0x64U < __VnbaIterCount)))) {
#ifdef VL_DEBUG
            Vtop___024root___dump_triggers__nba(vlSelf);
#endif
            VL_FATAL_MT("harness.v", 3, "", "NBA region did not converge.");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        __VnbaContinue = 0U;
        vlSelfRef.__VactIterCount = 0U;
        vlSelfRef.__VactContinue = 1U;
        while (vlSelfRef.__VactContinue) {
            if (VL_UNLIKELY(((0x64U < vlSelfRef.__VactIterCount)))) {
#ifdef VL_DEBUG
                Vtop___024root___dump_triggers__act(vlSelf);
#endif
                VL_FATAL_MT("harness.v", 3, "", "Active region did not converge.");
            }
            vlSelfRef.__VactIterCount = ((IData)(1U) 
                                         + vlSelfRef.__VactIterCount);
            vlSelfRef.__VactContinue = 0U;
            if (Vtop___024root___eval_phase__act(vlSelf)) {
                vlSelfRef.__VactContinue = 1U;
            }
        }
        if (Vtop___024root___eval_phase__nba(vlSelf)) {
            __VnbaContinue = 1U;
        }
    }
}

#ifdef VL_DEBUG
void Vtop___024root___eval_debug_assertions(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_debug_assertions\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}
#endif  // VL_DEBUG
