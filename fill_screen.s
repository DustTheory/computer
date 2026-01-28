# Fill screen with white pattern and configure VDMA
# Memory map:
#   Framebuffer 0: 0x87F1E000 (640x480x16bpp = 614,400 bytes)
#   VDMA Control:  0x88000000

.section .text
.globl _start

_start:
    # Load framebuffer base address (0x87F1E000) into t0
    lui t0, 0x87F1E          # t0 = 0x87F1E000

    # Load white pixel pattern (0xFFFFFFFF = two white pixels) into t2
    lui t2, 0xFFFFF          # t2 = 0xFFFFF000
    addi t2, t2, -1          # t2 = 0xFFFFFFFF

    # Loop counter: Fill 153600 words (entire framebuffer)
    # We'll count down from 153600 (0x25800)
    lui t1, 0x26             # t1 = 0x26000
    addi t1, t1, -0x800      # t1 = 0x25800 = 153600

fill_loop:
    sw t2, 0(t0)             # Store white pixels to framebuffer
    addi t0, t0, 4           # Increment address by 4 bytes
    addi t1, t1, -1          # Decrement counter
    bne t1, zero, fill_loop  # Continue if counter != 0

configure_vdma:
    # Load VDMA base address (0x88000000) into t3
    lui t3, 0x88000          # t3 = 0x88000000

    # Set MM2S_START_ADDRESS register (offset 0x18)
    # Value: 0x87F1E000 (framebuffer 0 address)
    lui t4, 0x87F1E          # t4 = 0x87F1E000
    sw t4, 0x18(t3)          # MM2S_START_ADDRESS[0] = 0x87F1E000

    # Set MM2S_HSIZE register (offset 0x24)
    # Value: 1280 (640 pixels * 2 bytes/pixel) = 0x500
    lui t4, 0                # Clear t4
    addi t4, zero, 0x500     # t4 = 1280
    sw t4, 0x24(t3)          # MM2S_HSIZE = 1280

    # Set MM2S_STRIDE register (offset 0x28)
    # Value: 1280 (same as HSIZE, no padding) = 0x500
    sw t4, 0x28(t3)          # MM2S_STRIDE = 1280 (reuse t4)

    # Set MM2S_VSIZE register (offset 0x20) - this triggers the transfer
    # Value: 480 (number of lines) = 0x1E0
    addi t4, zero, 0x1E0     # t4 = 480
    sw t4, 0x20(t3)          # MM2S_VSIZE = 480

    # Start VDMA by setting MM2S_VDMACR register (offset 0x00)
    # Bit 0: Run/Stop (1 = run)
    # Bit 1: Circular mode (1 = circular)
    # Bit 2: Reset (0 = normal)
    # Bit 3: GenLock Enable (0 = disable)
    # Bit 4: FrameCntEn (1 = enable)
    # Value: 0x00000013 (Run + Circular + FrameCntEn)
    lui t4, 0                # Clear t4
    addi t4, zero, 0x13      # t4 = 0x13
    sw t4, 0x00(t3)          # MM2S_VDMACR = 0x13

done:
    # Loop forever
    j done
