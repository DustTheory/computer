`timescale 1ns / 1ps

module reset_timer #(
    parameter COUNTER_WIDTH = 15,
    parameter HOLD_CYCLES   = 20000  // 200us at 100 MHz = 20,000 cycles
) (
    input i_Clock,
    input i_Enable,
    output reg o_Mig_Reset
);

  reg [COUNTER_WIDTH-1:0] r_Counter;

  initial begin
    r_Counter   = 0;
    o_Mig_Reset = 0;
  end

  always @(posedge i_Clock) begin
    if (!i_Enable) begin
      r_Counter   <= 0;
      o_Mig_Reset <= 0;
    end else if (r_Counter < HOLD_CYCLES) begin
      r_Counter   <= r_Counter + 1;
      o_Mig_Reset <= 0;
    end else begin
      r_Counter   <= r_Counter;
      o_Mig_Reset <= 1;
    end
  end

endmodule
