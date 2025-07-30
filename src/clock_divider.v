`timescale 1ns / 1ps

module clock_divider(
    input i_Clock,
    output o_Clock
  );
  reg [1:0] r_Clock_Count;
  always @(posedge i_Clock) r_Clock_Count <= r_Clock_Count + 1;
  assign o_Clock = r_Clock_Count[1];

endmodule
