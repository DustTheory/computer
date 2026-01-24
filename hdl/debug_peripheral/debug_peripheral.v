`timescale 1ns / 1ps
`include "cpu_core_params.vh"
`include "debug_peripheral.vh"

module debug_peripheral (
    input i_Clock,
    input i_Reset,

    input  i_Uart_Tx_In,
    output o_Uart_Rx_Out,

    input [31:0] i_PC,
    input i_Pipeline_Flushed,

    output reg o_Halt_Cpu,
    output reg o_Reset_Cpu,

    output reg o_Reg_Write_Enable,
    output reg [4:0] o_Reg_Write_Addr,
    output reg [31:0] o_Reg_Write_Data,

    output reg o_Reg_Read_Enable,
    output reg [4:0] o_Reg_Read_Addr,
    input [31:0] i_Reg_Read_Data,

    output reg o_Write_PC_Enable,
    output reg [31:0] o_Write_PC_Data

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

  // Input buffer (Stack)
  reg [7:0] input_buffer[0:255];
  reg [7:0] input_buffer_head = 0;

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
      input_buffer_head <= 0;
      o_Write_PC_Enable <= 0;
      o_Write_PC_Data <= 0;
    end else begin
      case (r_State)
        s_IDLE: begin
          if (w_Rx_DV) begin
            r_Op_Code <= w_Rx_Byte;
            r_State <= s_DECODE_AND_EXECUTE;
            r_Exec_Counter <= 0;
            input_buffer_head <= 0;
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
              o_Halt_Cpu <= 1;
              if (w_Rx_DV) begin
                input_buffer[input_buffer_head] <= w_Rx_Byte;
                input_buffer_head <= input_buffer_head + 1;
              end
              if (i_Pipeline_Flushed && input_buffer_head == 4) begin
                o_Write_PC_Enable <= 1;
                o_Write_PC_Data <= {
                  input_buffer[3], input_buffer[2], input_buffer[1], input_buffer[0]
                };
                input_buffer_head <= input_buffer_head + 1;
              end
              if (i_Pipeline_Flushed && input_buffer_head == 5) begin
                o_Write_PC_Enable <= 0;
                r_State <= s_IDLE;
              end
            end
            op_READ_REGISTER: begin
              o_Halt_Cpu <= 1;
              if (w_Rx_DV) begin
                input_buffer[input_buffer_head] <= w_Rx_Byte;
                input_buffer_head <= input_buffer_head + 1;
              end
              if (i_Pipeline_Flushed && input_buffer_head > 0) begin
                // Read register
                o_Reg_Read_Enable <= 1;
                o_Reg_Read_Addr   <= input_buffer[0][4:0];
                if (o_Reg_Read_Enable) begin
                  // Already got reg data, write it to the output
                  output_buffer[output_buffer_head] <= i_Reg_Read_Data[7:0];
                  output_buffer[output_buffer_head+1] <= i_Reg_Read_Data[15:8];
                  output_buffer[output_buffer_head+2] <= i_Reg_Read_Data[23:16];
                  output_buffer[output_buffer_head+3] <= i_Reg_Read_Data[31:24];
                  output_buffer_head <= output_buffer_head + 4;
                  o_Reg_Read_Enable <= 0;
                  r_State <= s_IDLE;
                end
              end
            end
            op_WRITE_REGISTER: begin
              o_Halt_Cpu <= 1;
              if (w_Rx_DV) begin
                input_buffer[input_buffer_head] <= w_Rx_Byte;
                input_buffer_head <= input_buffer_head + 1;
              end
              if (i_Pipeline_Flushed && input_buffer_head == 5) begin
                o_Reg_Write_Enable <= 1;
                o_Reg_Write_Addr <= input_buffer[0][4:0];
                o_Reg_Write_Data <= {
                  input_buffer[4], input_buffer[3], input_buffer[2], input_buffer[1]
                };
                input_buffer_head <= input_buffer_head + 1;
              end
              if (i_Pipeline_Flushed && input_buffer_head == 6) begin
                o_Reg_Write_Enable <= 0;
                r_State <= s_IDLE;
              end
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
