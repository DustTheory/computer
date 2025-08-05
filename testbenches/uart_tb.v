
`timescale 1ns / 1ps

module uart_tb ();
  localparam CLOCK_FREQUENCY = 100_000_000;
  localparam UART_BAUD_RATE = 115200;
  localparam UART_CLOCKS_PER_BIT = CLOCK_FREQUENCY/UART_BAUD_RATE;

  reg r_Clock = 0;
  reg r_Rx_Serial = 1;
  wire w_Rx_DV;
  wire [7:0] w_Rx_Byte;

  // 100MHz clock: toggles every 10ns
  always #5 r_Clock = ~r_Clock;

  uart_receiver #(.CLKS_PER_BIT(UART_CLOCKS_PER_BIT)) UART_RECEIVER(
                  .i_Clock(r_Clock),
                  .i_Rx_Serial(r_Rx_Serial),
                  .o_Rx_DV(w_Rx_DV),
                  .o_Rx_Byte(w_Rx_Byte)
                );


  wire [2:0] state = UART_RECEIVER.r_SM_Main;
  wire w_Rx_Data = UART_RECEIVER.r_Rx_Data;
  wire [15:0] w_Clock_Count = UART_RECEIVER.r_Clock_Count;

  initial
  begin
    //    $display("time,\th,\tv,\trgb");
    # 10;
    r_Rx_Serial = 0;
    # 10;
    r_Rx_Serial = 1;
    # 4350;
    r_Rx_Serial = 0;
    # 4350;
    r_Rx_Serial = 1;
    # 4350;
    r_Rx_Serial = 0;
    # 4350;
    r_Rx_Serial = 1;
    # 4350;
    r_Rx_Serial = 0;
    # 4350;
    r_Rx_Serial = 1;
    # 4350;
    r_Rx_Serial = 0;
    # 4350;
    r_Rx_Serial = 1;

    #1000 $finish;
  end


endmodule
