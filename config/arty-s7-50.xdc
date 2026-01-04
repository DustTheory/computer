set_property PACKAGE_PIN R2 [get_ports clk_in1_0]
set_property IOSTANDARD SSTL15 [get_ports clk_in1_0]

set_property PACKAGE_PIN V14 [get_ports ext_reset_in_0]
set_property IOSTANDARD LVCMOS33 [get_ports ext_reset_in_0]

set_property PACKAGE_PIN V12 [get_ports i_Uart_Tx_In_0]
set_property IOSTANDARD LVCMOS33 [get_ports i_Uart_Tx_In_0]

set_property IOSTANDARD LVCMOS33 [get_ports o_Uart_Rx_Out_0]
set_property PACKAGE_PIN R12 [get_ports o_Uart_Rx_Out_0]

# Clock routing constraint - allows BACKBONE routing for clock input to MMCM
# This is required because the clock input pin (R2) and MMCM are in different clock regions
set_property CLOCK_DEDICATED_ROUTE BACKBONE [get_nets computer_i/clk_wiz_0/inst/clk_in1_computer_clk_wiz_0_0]
