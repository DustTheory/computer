`timescale 1ns / 1ps

module gpu(
    input i_Clock,
    input i_Uart_Tx_In,
    output o_Horizontal_Sync,
    output o_Vertical_Sync,
    output [2:0] o_RGB
  );

  parameter CLOCK_FREQUENCY = 100_000_000;
  parameter UART_BAUD_RATE = 115200;
  parameter UART_CLOCKS_PER_BIT = CLOCK_FREQUENCY/UART_BAUD_RATE;

  parameter RESOLUTION_W = 640;
  parameter RESOLUTION_H = 480;
  parameter FRAMEBUFFER_DEPTH = RESOLUTION_W*RESOLUTION_H;
  parameter BITS_PER_PIXEL = 3;

  wire w_Vga_Out_Clock;
  clock_divider CLK_DIVIDER (
                  .i_Clock(i_Clock),
                  .o_Clock(w_Vga_Out_Clock)
                );

  wire w_Rx_DV;
  wire [7:0] w_Rx_Byte;
  uart_receiver #(.CLKS_PER_BIT(UART_CLOCKS_PER_BIT)) UART_RECEIVER(
                  .i_Clock(i_Clock),
                  .i_Rx_Serial(i_Uart_Tx_In),
                  .o_Rx_DV(w_Rx_DV),
                  .o_Rx_Byte(w_Rx_Byte)
                );

  wire [$clog2(FRAMEBUFFER_DEPTH - 1):0] w_Read_Addr;
  wire [BITS_PER_PIXEL-1:0] w_Read_Data;
  wire w_Write_Enable = 0;
  framebuffer #(
                .BITS_PER_PIXEL(BITS_PER_PIXEL),
                .FRAMEBUFFER_DEPTH(FRAMEBUFFER_DEPTH)
              ) FRAMEBUFFER(
                .i_Clock(i_Clock),
                .i_Read_Addr(w_Read_Addr),
                .i_Write_Enable(w_Write_Enable),
                .i_Write_Addr(r_Write_Addr),
                .i_Write_Data(w_Rx_Byte),
                .o_Read_Data(w_Read_Data)
              );

  // evil_state_machine #(
  //                      .BITS_PER_PIXEL(BITS_PER_PIXEL),
  //                      .FRAMEBUFFER_DEPTH(FRAMEBUFFER_DEPTH)
  //                    ) EVIL_STATE_MACHINE(
  //                      .i_Clock(CLK100MHZ),
  //                      .i_Rx_Byte(w_Rx_Byte),
  //                      .o_Write_Addr(w_Write_Addr),
  //                      .o_Write_Data(w_Write_Data)
  //                    );

  vga_out  #(
             .BITS_PER_PIXEL(BITS_PER_PIXEL),
             .FRAMEBUFFER_DEPTH(FRAMEBUFFER_DEPTH)
           ) VGA_OUT(
             .clk(w_Vga_Out_Clock),
             .i_Fb_Read_Data(w_Rx_Byte),
             .o_Fb_Read_Addr(w_Read_Addr),
             .o_Horizontal_Sync(o_Horizontal_Sync),
             .o_Vertical_Sync(o_Vertical_Sync),
             .o_RGB(o_RGB)
           );

endmodule
