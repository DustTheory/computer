`timescale 1ns / 1ps

module gpu(
    input i_Clock,
    input i_Uart_Tx_In,
    output o_Horizontal_Sync,
    output o_Vertical_Sync,
    output [2:0] o_RGB,
    output o_Write_Enable
  );

  localparam CLOCK_FREQUENCY = 100_000_000;
  localparam UART_BAUD_RATE = 115200;
  localparam UART_CLOCKS_PER_BIT = (CLOCK_FREQUENCY/UART_BAUD_RATE);

  localparam RESOLUTION_W = 640;
  localparam RESOLUTION_H = 480;
  localparam FRAMEBUFFER_DEPTH = RESOLUTION_W*RESOLUTION_H;
  localparam BITS_PER_PIXEL = 3;

  wire w_Rx_DV;
  wire [7:0] w_Rx_Byte;
  uart_receiver #(.CLKS_PER_BIT(UART_CLOCKS_PER_BIT)) UART_RECEIVER(
                  .i_Clock(i_Clock),
                  .i_Rx_Serial(i_Uart_Tx_In),
                  .o_Rx_DV(w_Rx_DV),
                  .o_Rx_Byte(w_Rx_Byte)
                );

  wire [31:0] w_Read_Addr;
  wire [BITS_PER_PIXEL-1:0] w_Read_Data;
  wire [BITS_PER_PIXEL-1:0] w_Write_Data;
  wire [31:0] w_Write_Addr;
  wire w_Write_Enable;
  framebuffer #(
                .BITS_PER_PIXEL(BITS_PER_PIXEL),
                .FRAMEBUFFER_DEPTH(FRAMEBUFFER_DEPTH)
              ) FRAMEBUFFER(
                .i_Clock(i_Clock),
                .i_Read_Addr(w_Read_Addr),
                .i_Write_Enable(w_Write_Enable),
                .i_Write_Addr(w_Write_Addr),
                .i_Write_Data(w_Write_Data),
                .o_Read_Data(w_Read_Data)
              );

  instruction_engine #(
                       .BITS_PER_PIXEL(BITS_PER_PIXEL),
                       .FRAMEBUFFER_DEPTH(FRAMEBUFFER_DEPTH)
                     ) INSTRUCTION_ENGINE(
                       .i_Clock(i_Clock),
                       .i_Rx_DV(w_Rx_DV),
                       .i_Rx_Byte(w_Rx_Byte),
                       .o_Write_Enable(w_Write_Enable),
                       .o_Write_Addr(w_Write_Addr),
                       .o_Write_Data(w_Write_Data)
                     );

  vga_out  #(
             .BITS_PER_PIXEL(BITS_PER_PIXEL),
             .FRAMEBUFFER_DEPTH(FRAMEBUFFER_DEPTH)
           ) VGA_OUT(
             .i_Clock(i_Clock),
             .i_Fb_Read_Data(w_Read_Data),
             .o_Fb_Read_Addr(w_Read_Addr),
             .o_Horizontal_Sync(o_Horizontal_Sync),
             .o_Vertical_Sync(o_Vertical_Sync),
             .o_RGB(o_RGB)
           );


  // cpu CPU(
  //       .i_Clock(i_Clock),
  //       .i_Write_Enable(w_Write_Enable),
  //       .i_Load_Store_Type(3'b101), // LS_TYPE_STORE_WORD
  //       .i_Instruction_Addr(32'b0),
  //       .i_Data_Addr(32'b0),
  //       .i_Write_Data(32'b0),
  //       .o_Read_Data(),
  //       .o_Instruction()
  //     );

  assign o_Write_Enable = w_Write_Enable;

endmodule
