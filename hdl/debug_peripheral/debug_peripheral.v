`timescale 1ns / 1ps
`include "cpu_core_params.vh"
`include "debug_peripheral.vh"

module debug_peripheral (
    input i_Clock,
    input i_Reset,

    input  i_Uart_Tx_In,
    output o_Uart_Rx_Out,

    input [31:0] i_PC,

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

  /* ----------------UART_TRANSMITTER---------------- */

  // Output buffer (FIFO)
  reg [7:0] output_buffer[0:255];
  reg [7:0] output_buffer_head = 0;
  reg [7:0] output_buffer_tail = 0;

  reg r_Tx_DV;
  reg [7:0] r_Tx_Byte = 0;
  wire w_Tx_Done;

  uart_transmitter uart_transmitter (
      .i_Reset(i_Reset),
      .i_Clock(i_Clock),
      .i_Tx_DV(r_Tx_DV),
      .i_Tx_Byte(r_Tx_Byte),
      .o_Tx_Serial(o_Uart_Rx_Out),
      .o_Tx_Done(w_Tx_Done)
  );

  always @(posedge i_Clock, posedge i_Reset) begin
    if (i_Reset) begin
      r_Tx_DV <= 0;
      r_Tx_Byte <= 0;
      output_buffer_tail <= 0;
    end else begin
      if (!r_Tx_DV && (output_buffer_head != output_buffer_tail)) begin
        r_Tx_Byte <= output_buffer[output_buffer_tail];
        r_Tx_DV <= 1;
        output_buffer_tail <= output_buffer_tail + 1;
      end else if (w_Tx_Done) begin
        r_Tx_DV   <= 0;
        r_Tx_Byte <= 0;
      end
    end
  end

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
      r_Exec_Counter <= 0;
      output_buffer_head <= 0;
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
          case (r_Op_Code)
            op_NOP: begin
              // Do nothing
              r_State <= s_IDLE;
            end
            op_RESET: begin
              o_Reset_Cpu <= 1;
              r_State <= s_IDLE;
            end
            op_UNRESET: begin
              o_Reset_Cpu <= 0;
              r_State <= s_IDLE;
            end
            op_HALT: begin
              o_Halt_Cpu <= 1;
              r_State <= s_IDLE;
            end
            op_UNHALT: begin
              o_Halt_Cpu <= 0;
              r_State <= s_IDLE;
            end
            op_PING: begin
              output_buffer[output_buffer_head] <= PING_RESPONSE_BYTE;
              output_buffer_head <= output_buffer_head + 1;
              r_State <= s_IDLE;
            end
            op_READ_PC: begin
              case (r_Exec_Counter)
                0: begin
                  output_buffer[output_buffer_head] <= i_PC[7:0];
                  output_buffer_head <= output_buffer_head + 1;
                end
                1: begin
                  output_buffer[output_buffer_head] <= i_PC[15:8];
                  output_buffer_head <= output_buffer_head + 1;
                end
                2: begin
                  output_buffer[output_buffer_head] <= i_PC[23:16];
                  output_buffer_head <= output_buffer_head + 1;
                end
                3: begin
                  output_buffer[output_buffer_head] <= i_PC[31:24];
                  output_buffer_head <= output_buffer_head + 1;
                end
                default: begin
                  r_State <= s_IDLE;
                end
              endcase
            end
            op_WRITE_PC: begin
              // To be implemented
              r_State <= s_IDLE;
            end
            op_READ_REGISTER: begin
              // To be implemented
              r_State <= s_IDLE;
            end
            op_WRITE_REGISTER: begin
              // To be implemented
              r_State <= s_IDLE;
            end
            default: begin
              r_State <= s_IDLE;
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
