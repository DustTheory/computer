`timescale 1ns / 1ps
`include "cpu_core_params.vh"

module uart_transmitter (
    input i_Reset,
    input i_Clock,
    input i_Tx_DV,
    input [7:0] i_Tx_Byte,
    output reg o_Tx_Serial,
    output reg o_Tx_Done
);

  localparam s_IDLE = 3'b000;
  localparam s_TX_START_BIT = 3'b001;
  localparam s_TX_DATA_BITS = 3'b010;
  localparam s_TX_STOP_BIT = 3'b011;
  localparam s_CLEANUP = 3'b100;

  reg [ 7:0] r_Tx_Byte = 0;
  reg [ 2:0] r_SM_Main = s_IDLE;
  reg [15:0] r_Clock_Count = 0;
  reg [ 2:0] r_Bit_Index = 0;

  always @(posedge i_Clock) begin
    if (i_Reset) begin
      r_SM_Main     <= s_IDLE;
      r_Clock_Count <= 0;
      r_Bit_Index   <= 0;
      r_Tx_Byte     <= 0;
      o_Tx_Serial   <= 1'b1;  // Idle state is high
      o_Tx_Done     <= 1'b0;
    end else begin
      case (r_SM_Main)
        s_IDLE: begin
          o_Tx_Done     <= 0;
          r_Clock_Count <= 0;
          r_Bit_Index   <= 0;
          o_Tx_Serial   <= 1'b1;  // Idle state is high
          if (i_Tx_DV == 1'b1) begin
            r_SM_Main <= s_TX_START_BIT;
            r_Tx_Byte <= i_Tx_Byte;
          end else begin
            r_SM_Main <= s_IDLE;
            r_Tx_Byte <= 0;
          end
        end
        s_TX_START_BIT: begin
          o_Tx_Serial <= 1'b0;  // Start bit
          if (r_Clock_Count < UART_CLOCKS_PER_BIT[15:0] - 1) begin
            r_Clock_Count <= r_Clock_Count + 1;
            r_SM_Main <= s_TX_START_BIT;
          end else begin
            r_Clock_Count <= 0;
            r_SM_Main <= s_TX_DATA_BITS;
          end
        end
        s_TX_DATA_BITS: begin
          o_Tx_Serial <= r_Tx_Byte[r_Bit_Index];
          if (r_Clock_Count < UART_CLOCKS_PER_BIT[15:0] - 1) begin
            r_Clock_Count <= r_Clock_Count + 1;
            r_SM_Main <= s_TX_DATA_BITS;
          end else begin
            r_Clock_Count <= 0;
            if (r_Bit_Index < 7) begin
              r_Bit_Index <= r_Bit_Index + 1;
              r_SM_Main   <= s_TX_DATA_BITS;
            end else begin
              r_Bit_Index <= 0;
              r_SM_Main   <= s_TX_STOP_BIT;
            end
          end
        end
        s_TX_STOP_BIT: begin
          o_Tx_Serial <= 1'b1;  // Stop bit
          if (r_Clock_Count < UART_CLOCKS_PER_BIT[15:0] - 1) begin
            r_Clock_Count <= r_Clock_Count + 1;
            r_SM_Main <= s_TX_STOP_BIT;
          end else begin
            r_Clock_Count <= 0;
            r_SM_Main <= s_CLEANUP;
            o_Tx_Done <= 1'b1;
          end
        end
        s_CLEANUP: begin
          r_SM_Main <= s_IDLE;
          o_Tx_Done <= 1'b1;
        end
        default: begin
          r_SM_Main <= s_IDLE;
        end
      endcase
    end
  end


endmodule
