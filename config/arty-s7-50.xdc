set_property PACKAGE_PIN F14 [get_ports clk_in1_0]
set_property IOSTANDARD LVCMOS33 [get_ports clk_in1_0]

set_property PACKAGE_PIN V14 [get_ports ext_reset_in_0]
set_property IOSTANDARD LVCMOS33 [get_ports ext_reset_in_0]
set_property PULLTYPE PULLUP [get_ports ext_reset_in_0]

set_property PACKAGE_PIN V12 [get_ports i_Uart_Tx_In_0]
set_property IOSTANDARD LVCMOS33 [get_ports i_Uart_Tx_In_0]

set_property IOSTANDARD LVCMOS33 [get_ports o_Uart_Rx_Out_0]
set_property PACKAGE_PIN R12 [get_ports o_Uart_Rx_Out_0]

## Pmod Header JA
set_property -dict { PACKAGE_PIN L17   IOSTANDARD LVCMOS33 } [get_ports { o_Red_1[0]  }]; #IO_L4P_T0_D04_14 Sch=ja_p[1]
set_property -dict { PACKAGE_PIN L18   IOSTANDARD LVCMOS33 } [get_ports { o_Red_1[1]  }]; #IO_L4N_T0_D05_14 Sch=ja_n[1]
set_property -dict { PACKAGE_PIN M14   IOSTANDARD LVCMOS33 } [get_ports { o_Red_1[2]  }]; #IO_L5P_T0_D06_14 Sch=ja_p[2]
set_property -dict { PACKAGE_PIN N14   IOSTANDARD LVCMOS33 } [get_ports { o_Red_1[3]  }]; #IO_L5N_T0_D07_14 Sch=ja_n[2]
set_property -dict { PACKAGE_PIN M16   IOSTANDARD LVCMOS33 } [get_ports { o_Green_1[0] }]; #IO_L7P_T1_D09_14 Sch=ja_p[3]
set_property -dict { PACKAGE_PIN M17   IOSTANDARD LVCMOS33 } [get_ports { o_Green_1[1] }]; #IO_L7N_T1_D10_14 Sch=ja_n[3]
set_property -dict { PACKAGE_PIN M18   IOSTANDARD LVCMOS33 } [get_ports { o_Green_1[2] }]; #IO_L8P_T1_D11_14 Sch=ja_p[4]
set_property -dict { PACKAGE_PIN N18   IOSTANDARD LVCMOS33 } [get_ports { o_Green_1[3] }]; #IO_L8N_T1_D12_14 Sch=ja_n[4]

## Pmod Header JB
set_property -dict { PACKAGE_PIN P17   IOSTANDARD LVCMOS33 } [get_ports { o_Blue_1[0] }]; #IO_L9P_T1_DQS_14 Sch=jb_p[1]
set_property -dict { PACKAGE_PIN P18   IOSTANDARD LVCMOS33 } [get_ports { o_Blue_1[1] }]; #IO_L9N_T1_DQS_D13_14 Sch=jb_n[1]
set_property -dict { PACKAGE_PIN R18   IOSTANDARD LVCMOS33 } [get_ports { o_Blue_1[2] }]; #IO_L10P_T1_D14_14 Sch=jb_p[2]
set_property -dict { PACKAGE_PIN T18   IOSTANDARD LVCMOS33 } [get_ports { o_Blue_1[3] }]; #IO_L10N_T1_D15_14 Sch=jb_n[2]
set_property -dict { PACKAGE_PIN P14   IOSTANDARD LVCMOS33 } [get_ports { o_Horizontal_Sync_1 }]; #IO_L11P_T1_SRCC_14 Sch=jb_p[3]
set_property -dict { PACKAGE_PIN P15   IOSTANDARD LVCMOS33 } [get_ports { o_Vertical_Sync_1 }]; #IO_L11N_T1_SRCC_14 Sch=jb_n[3]