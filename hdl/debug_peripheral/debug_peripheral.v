`timescale 1ns / 1ps
`include "cpu_core_params.vh"
`include "debug_peripheral.vh"

module debug_peripheral (
    input i_Clock,
    input i_Reset,

    input i_Uart_Tx_In,

    output reg o_Halt_Cpu = 0,
    output reg o_Reset_Cpu = 0

    // output o_Reg_Write_Enable,
    // output [4:0] o_Reg_Write_Addr,
    // output [31:0] o_Reg_Write_Data,

    // output o_Reg_Read_Enable,
    // output [4:0] o_Reg_Read_Addr,
    // input [31:0] i_Reg_Read_Data

);

  /* ----------------UART RECEIVER---------------- */

  wire w_Rx_DV;
  wire [7:0] w_Rx_Byte;
  uart_receiver uart_receiver (
      .i_Reset(i_Reset),
      .i_Clock(i_Clock),
      .i_Rx_Serial(i_Uart_Tx_In),
      .o_Rx_DV(w_Rx_DV),
      .o_Rx_Byte(w_Rx_Byte)
  );

  /* ----------------DEBUG PERIPHERAL LOGIC---------------- */

  reg [ 1:0] r_State = s_IDLE;
  reg [ 7:0] r_Op_Code = 0;
  reg [31:0] r_Exec_Counter = 0;

  always @(posedge i_Clock, posedge i_Reset) begin
    if (i_Reset) begin
      r_State <= s_IDLE;
      r_Op_Code <= 0;
      o_Halt_Cpu <= 0;
      o_Reset_Cpu <= 0;
    end else begin
      case (r_State)
        s_IDLE: begin
          if (w_Rx_DV) begin
            r_Op_Code <= w_Rx_Byte;
            r_State <= s_DECODE_AND_EXECUTE;
            r_Exec_Counter <= 0;
          end
        end
        s_DECODE_AND_EXECUTE: begin
          r_State <= s_IDLE;
          case (r_Op_Code)
            op_NOP: begin
              // Do nothing
            end
            op_RESET: begin
              o_Reset_Cpu <= 1;
            end
            op_UNRESET: begin
              o_Reset_Cpu <= 0;
            end
            op_HALT: begin
              o_Halt_Cpu <= 1;
            end
            op_UNHALT: begin
              o_Halt_Cpu <= 0;
            end
            default: begin
              // Unknown op code, do nothing
            end
          endcase
          r_Exec_Counter <= r_Exec_Counter + 1;
        end
        default: begin
          r_State <= s_IDLE;
        end
      endcase
    end
  end

endmodule
