"""
Test to demonstrate pipeline flush and memory alignment issues
"""
import cocotb
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb.clock import Clock

# Quick test to demonstrate the pipeline flush issue
@cocotb.test()
async def test_branch_pipeline_flush_issue(dut):
    """Demonstrate that taken branches don't flush the pipeline"""

    clock = Clock(dut.i_Clock, 1, "ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 2)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 2)

    # Set PC to 0x1000 (DDR3 region to test alignment too)
    dut.cpu.r_PC.value = 0x1000

    # Manually inject a simple sequence:
    # 0x1000: BEQ R1, R1, +8    (always taken, jump to 0x1008)
    # 0x1004: ADD R2, R2, #1    (should be FLUSHED but probably executes)
    # 0x1008: ADD R3, R3, #1    (branch target, should execute)

    # Set R1=R1=1 (branch will be taken)
    dut.cpu.reg_file.Registers[1].value = 1
    dut.cpu.reg_file.Registers[2].value = 0  # Should remain 0 if flushed
    dut.cpu.reg_file.Registers[3].value = 0  # Should become 1

    # BEQ R1, R1, +8 (offset=8)
    # Format: imm[12|10:5] rs2[4:0] rs1[4:0] funct3[2:0] imm[4:1|11] opcode[6:0]
    # BEQ: opcode=1100011, funct3=000, rs1=1, rs2=1, imm=8
    beq_instruction = (0 << 31) | (0 << 30) | (0 << 29) | (0 << 28) | (0 << 27) | (0 << 26) | (0 << 25) | \
                      (1 << 20) | (1 << 15) | (0 << 12) | (0 << 11) | (0 << 10) | (0 << 9) | (0 << 8) | \
                      0b1100011

    # ADD R2, R2, #1 (ADDI)
    # Format: imm[11:0] rs1[4:0] funct3[2:0] rd[4:0] opcode[6:0]
    # ADDI: opcode=0010011, funct3=000, rd=2, rs1=2, imm=1
    addi_wrong_path = (1 << 20) | (2 << 15) | (0 << 12) | (2 << 7) | 0b0010011

    # ADD R3, R3, #1 (ADDI)
    addi_correct_path = (1 << 20) | (3 << 15) | (0 << 12) | (3 << 7) | 0b0010011

    # Write instructions to instruction RAM (simulating DDR3)
    # Note: This assumes the testbench has instruction_ram module
    try:
        # Write to instruction memory
        dut.instruction_ram.mem[0x1000 >> 2].value = beq_instruction
        dut.instruction_ram.mem[0x1004 >> 2].value = addi_wrong_path
        dut.instruction_ram.mem[0x1008 >> 2].value = addi_correct_path

        # Run for several cycles to see what happens
        await ClockCycles(dut.i_Clock, 20)

        print(f"After branch execution:")
        print(f"PC: 0x{dut.cpu.r_PC.value:08x}")
        print(f"R2 (should be 0 if flushed): {dut.cpu.reg_file.Registers[2].value}")
        print(f"R3 (should be 1): {dut.cpu.reg_file.Registers[3].value}")

        # Check results
        if dut.cpu.reg_file.Registers[2].value != 0:
            print("❌ PIPELINE FLUSH ISSUE: Wrong-path instruction executed!")
            print("   The ADD R2,R2,#1 at 0x1004 should have been flushed")
        else:
            print("✅ Pipeline flush working correctly")

        if dut.cpu.r_PC.value != 0x1008:
            print("❌ Branch target incorrect")
        else:
            print("✅ Branch target correct")

    except AttributeError:
        print("⚠️  Cannot access instruction_ram.mem - test setup issue")
        print("   This test needs access to instruction memory")

@cocotb.test()
async def test_memory_alignment_issue(dut):
    """Test if 16-bit vs 32-bit alignment affects instruction fetch"""

    clock = Clock(dut.i_Clock, 1, "ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 2)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 10)  # Wait for DDR3 calib

    print("Testing memory alignment...")

    # Test various alignments in DDR3 region (> 0x1000)
    test_addresses = [
        0x1000,  # 4-byte aligned
        0x1004,  # 4-byte aligned
        0x1002,  # 2-byte aligned (should work if MIG allows)
        0x1006,  # 2-byte aligned
    ]

    for addr in test_addresses:
        try:
            dut.cpu.r_PC.value = addr
            await ClockCycles(dut.i_Clock, 5)

            # Check if instruction fetch worked
            if dut.cpu.w_Instruction_Valid.value:
                print(f"✅ Address 0x{addr:04x}: Instruction fetch successful")
            else:
                print(f"❌ Address 0x{addr:04x}: Instruction fetch failed")

        except Exception as e:
            print(f"❌ Address 0x{addr:04x}: Exception - {e}")