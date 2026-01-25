#!/usr/bin/env python3
"""Batch update test files with halt/unhalt pattern."""

import re
import sys

files_to_update = [
    'test_ori', 'test_sub', 'test_xor', 'test_xori',
    'test_sll', 'test_slli', 'test_slt', 'test_slti', 'test_sltiu', 'test_sltu',
    'test_sra', 'test_srai', 'test_srl', 'test_srli',
    'test_lb', 'test_lbu', 'test_lh', 'test_lhu', 'test_lw',
    'test_sb', 'test_sh', 'test_sw',
    'test_lui', 'test_jal', 'test_jalr',
]

base_path = '/home/emma/gpu/tests/cpu/integration_tests/'

def update_file_with_halt_unhalt(filepath):
    """Add halt/unhalt pattern to test file."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Pattern 1: For files with loops (most R-type and I-type ALU instructions)
    # Match: await ClockCycles + write_word_to_mem + r_PC + registers + await ClockCycles(PIPELINE_CYCLES)
    pattern1 = re.compile(
        r'(\s+)(dut\.i_Reset\.value = 0\n\s+await ClockCycles\(dut\.i_Clock, 1\))\n\n'
        r'(\s+)((?:write_word_to_mem|write_byte_to_mem|write_half_to_mem)[^\n]+\n)'
        r'(\s+)(dut\.cpu\.r_PC\.value = [^\n]+\n)'
        r'((?:\s+dut\.cpu\.reg_file\.Registers\[[^\]]+\]\.value = [^\n]+\n)+)'
        r'(\s+)(await ClockCycles\(dut\.i_Clock, PIPELINE_CYCLES\))',
        re.MULTILINE
    )

    def replacement1(match):
        indent = match.group(1)
        reset_line = match.group(2)
        write_indent = match.group(3)
        write_line = match.group(4)
        pc_indent = match.group(5)
        pc_line = match.group(6)
        reg_lines = match.group(7)
        await_indent = match.group(8)
        await_line = match.group(9)

        return (
            f'{indent}{reset_line}\n\n'
            f'{indent}# HALT CPU before setup\n'
            f'{indent}await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_HALT)\n'
            f'{indent}await wait_for_pipeline_flush(dut)\n\n'
            f'{indent}# Set up test while CPU is halted\n'
            f'{write_indent}{write_line}'
            f'{pc_indent}{pc_line}'
            f'{reg_lines}'
            f'{await_indent}await ClockCycles(dut.i_Clock, 1)\n\n'
            f'{indent}# UNHALT CPU to start execution\n'
            f'{indent}await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_UNHALT)\n\n'
            f'{await_indent}{await_line.replace("PIPELINE_CYCLES)", "PIPELINE_CYCLES + 3)")}'
        )

    # Try pattern 1
    new_content, count = pattern1.subn(replacement1, content)

    if count > 0:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Updated {filepath} ({count} replacements)")
        return True
    else:
        print(f"No matches found in {filepath} - needs manual update")
        return False

if __name__ == '__main__':
    for fname in files_to_update:
        fpath = base_path + fname + '_instruction.py'
        try:
            update_file_with_halt_unhalt(fpath)
        except Exception as e:
            print(f"Error updating {fname}: {e}")
