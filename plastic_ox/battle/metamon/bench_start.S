.syntax unified
.cpu arm7tdmi
.arm
.section .text.start,"ax"
.global _start
_start:
    b boot
    .space 188
boot:
    mov r0, #0xdf
    msr cpsr_c, r0
    ldr sp, =0x03007f00
    ldr r0, =__iwram_load
    ldr r1, =__iwram_start
    ldr r2, =__iwram_end
1:
    cmp r1, r2
    ldrlo r3, [r0], #4
    strlo r3, [r1], #4
    blo 1b
    ldr r0, =__data_load
    ldr r1, =__data_start
    ldr r2, =__data_end
2:
    cmp r1, r2
    ldrlo r3, [r0], #4
    strlo r3, [r1], #4
    blo 2b
    mov r0, #0
    ldr r1, =__bss_start
    ldr r2, =__bss_end
3:
    cmp r1, r2
    strlo r0, [r1], #4
    blo 3b
    ldr r0, =main
    bx r0
