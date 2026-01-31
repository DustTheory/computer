`timescale 1ns / 1ps
`include "cpu_core_params.vh"
`include "debug_peripheral.vh"
`include "memory.vh"

module debug_peripheral (
    input i_Clock,
    input i_Reset,

    input  i_Uart_Tx_In,
    output o_Uart_Rx_Out,

    input [XLEN-1:0] i_PC,
    input i_Pipeline_Flushed,

    output reg o_Halt_Cpu,
    output reg o_Reset_Cpu,

    output reg o_Reg_Write_Enable,
    output reg [4:0] o_Reg_Write_Addr,
    output reg [XLEN-1:0] o_Reg_Write_Data,

    output reg o_Reg_Read_Enable,
    output reg [4:0] o_Reg_Read_Addr,
    input [XLEN-1:0] i_Reg_Read_Data,

    output reg o_Write_PC_Enable,
    output reg [XLEN-1:0] o_Write_PC_Data,

    output reg o_Memory_LS_Enable,
    output reg [LS_SEL_WIDTH:0] o_Memory_LS_Type,
    output reg o_Memory_LS_Write_Enable,
    output reg [XLEN-1:0] o_Memory_LS_Address,
    output reg [XLEN-1:0] o_Memory_LS_Data,
    input [XLEN-1:0] i_Memory_Data_Out,
    input [MEMORY_STATE_WIDTH:0] i_Memory_State

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
  reg [7:0] input_buffer[0:4100]; // An entire page of memory + slack
  reg [7:0] input_buffer_head = 0;

  // Output buffer (FIFO)
  reg [7:0] output_buffer[0:4100]; // An entire page of memory + slack
  reg [7:0] output_buffer_head = 0;
  reg [7:0] output_buffer_tail = 0;

  // Memory Operation States
  reg [15:0] r_Bytes_Remaining = 0;
  reg [XLEN-1:0] r_Memory_Address = 0;

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
      o_Memory_LS_Address <= 0;
      o_Memory_LS_Data <= 0;
      o_Memory_LS_Type <= LS_TYPE_NONE;
      o_Memory_LS_Enable <= 0;
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
            op_READ_MEMORY: begin
              o_Halt_Cpu <= 1;
              o_Memory_LS_Enable <= 1;
              if(w_Rx_DV && input_buffer_head < 8) begin
                input_buffer[input_buffer_head] <= w_Rx_Byte;
                input_buffer_head <= input_buffer_head + 1;
              end
              if(i_Pipeline_Flushed && input_buffer_head == 7) begin
                r_Memory_Address <= {
                  input_buffer[3], input_buffer[2], input_buffer[1], input_buffer[0]
                };
                r_Bytes_Remaining <= {input_buffer[5], input_buffer[4]};
                input_buffer_head <= input_buffer_head + 1;
              end
              if(i_Pipeline_Flushed && r_Bytes_Remaining > 0) begin
                case (i_Memory_State)
                    IDLE: begin
                      o_Memory_LS_Address <= r_Memory_Address;
                      case(r_Bytes_Remaining & 0'b11)
                        1: o_Memory_LS_Type    <= LS_BYTE;
                        2: o_Memory_LS_Type    <= LS_HALFWORD;
                        default: o_Memory_LS_Type    <= LS_WORD;
                      endcase
                    end
                    READ_SUBMITTING, READ_AWAITING: begin
                      // Don't issue any more commands while waiting
                      o_Memory_LS_Address <= 0;
                      o_Memory_LS_Type    <= LS_TYPE_NONE;
                    end
                    READ_SUCCESS: begin
                      o_Memory_LS_Address <= 0;
                      o_Memory_LS_Type    <= LS_TYPE_NONE;
                      case (r_Bytes_Remaining & 0'b11)
                        1: begin
                          output_buffer[output_buffer_head] <= i_Memory_Data_Out[7:0];
                          output_buffer_head <= output_buffer_head + 1;
                          r_Bytes_Remaining <= r_Bytes_Remaining - 1;
                          r_Memory_Address   <= r_Memory_Address + 1;
                        end
                        2: begin
                          output_buffer[output_buffer_head] <= i_Memory_Data_Out[7:0];
                          output_buffer[output_buffer_head+1] <= i_Memory_Data_Out[15:8];
                          output_buffer_head <= output_buffer_head + 2;
                          r_Bytes_Remaining <= r_Bytes_Remaining - 2;
                          r_Memory_Address   <= r_Memory_Address + 2;
                        end
                        default: begin
                          output_buffer[output_buffer_head] <= i_Memory_Data_Out[7:0];
                          output_buffer[output_buffer_head+1] <= i_Memory_Data_Out[15:8];
                          output_buffer[output_buffer_head+2] <= i_Memory_Data_Out[23:16];
                          output_buffer[output_buffer_head+3] <= i_Memory_Data_Out[31:24];
                          output_buffer_head <= output_buffer_head + 4;
                          r_Bytes_Remaining <= r_Bytes_Remaining - 4;
                          r_Memory_Address   <= r_Memory_Address + 4;
                        end
                      endcase
                    end
                    default: begin
                      // Invald memory state for read
                      output_buffer[output_buffer_head] <= MEMORY_READ_ERROR_STRING[7:0];
                      output_buffer[output_buffer_head+1] <= MEMORY_READ_ERROR_STRING[15:8];
                      output_buffer[output_buffer_head+2] <= MEMORY_READ_ERROR_STRING[23:16];
                      output_buffer[output_buffer_head+3] <= MEMORY_READ_ERROR_STRING[31:24];
                      output_buffer_head <= output_buffer_head + 4;
                      o_Memory_LS_Address <= 0;
                      o_Memory_LS_Type    <= LS_TYPE_NONE;
                    end
                  end
              end
              if(input_buffer_head == 8 && r_Bytes_Remaining == 0) begin
                o_Memory_LS_Enable <= 0;
                o_Memory_LS_Type <= LS_TYPE_NONE;
                r_State <= s_IDLE;
              end
            end
            op_WRITE_MEMORY: begin
              // Receive 4 bytes of address
              // Then 2 bytes for length of data to write
              // Then the data
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
