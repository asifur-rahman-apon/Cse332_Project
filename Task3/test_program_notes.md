# CPU Test Program

Load `test_program.hex` into the instruction ROM: right-click the ROM, choose Load Image, and select the file. The program has 41 instructions (addresses 0 to 40) and writes nothing to RAM beforehand. It stores values with SW and reads them back with LW.

The ROM must use 10-bit data width and at least 6 address bits. The program was assembled with the updated opcodes and checked with a software simulation of the ISA.

## Program

| Addr | Instruction | Binary | Hex | Effect |
|---|---|---|---|---|
| 0 | ADDI R1, 3 | 0001001011 | 04b | R1 = 3 |
| 1 | ADDI R2, 2 | 0001010010 | 052 | R2 = 2 |
| 2 | ADD R1, R2 | 0000001010 | 00a | R1 = 5 |
| 3 | SUB R2, R1 | 0100010001 | 111 | R2 = 2 - 5 = -3 (0x3FD) |
| 4 | ADDI R3, 3 | 0001011011 | 05b | R3 = 3 |
| 5 | AND R3, R1 | 0010011001 | 099 | R3 = 3 & 5 = 1 |
| 6 | ADDI R4, 2 | 0001100010 | 062 | R4 = 2 |
| 7 | OR R4, R1 | 0011100001 | 0e1 | R4 = 2 | 5 = 7 |
| 8 | SLL R1, R3 | 0110001011 | 18b | R1 = 5 << 1 = 10 |
| 9 | CMP R3, R4 | 0101011100 | 15c | 1 < 7: E=0, L=1 |
| 10 | BLT 1 | 1101000001 | 341 | taken, skips next |
| 11 | ADDI R5, 3 | 0001101011 | 06b | SKIPPED (poison) |
| 12 | ADDI R5, 1 | 0001101001 | 069 | R5 = 1 |
| 13 | CMP R3, R3 | 0101011011 | 15b | E=1, L=0 |
| 14 | BEQ 1 | 1100000001 | 301 | taken, skips next |
| 15 | ADDI R6, 3 | 0001110011 | 073 | SKIPPED (poison) |
| 16 | ADDI R6, 2 | 0001110010 | 072 | R6 = 2 |
| 17 | CMP R3, R4 | 0101011100 | 15c | E=0, L=1 |
| 18 | BEQ 1 | 1100000001 | 301 | NOT taken |
| 19 | ADDI R6, 1 | 0001110001 | 071 | R6 = 3 (runs because BEQ not taken) |
| 20 | CMP R2, R3 | 0101010011 | 153 | -3 < 1 signed: L=1 |
| 21 | BLT 1 | 1101000001 | 341 | taken, skips next |
| 22 | ADDI R5, 3 | 0001101011 | 06b | SKIPPED (poison) |
| 23 | ADDI R5, 1 | 0001101001 | 069 | R5 = 2 |
| 24 | JMP 1 | 1110000001 | 381 | skips next |
| 25 | ADDI R5, 3 | 0001101011 | 06b | SKIPPED (poison) |
| 26 | ADDI R7, 3 | 0001111011 | 07b | R7 = 3 (base address) |
| 27 | SW R1, 0 | 1001001000 | 248 | Mem[3] = R1 = 10 |
| 28 | SW R4, 1 | 1001100001 | 261 | Mem[4] = R4 = 7 |
| 29 | SW R2, -1 | 1001010111 | 257 | Mem[2] = R2 = 0x3FD (negative offset) |
| 30 | LW R5, 0 | 1000101000 | 228 | R5 = Mem[3] = 10 |
| 31 | LW R6, 1 | 1000110001 | 231 | R6 = Mem[4] = 7 |
| 32 | LW R3, -1 | 1000011111 | 21f | R3 = Mem[2] = 0x3FD |
| 33 | OUT R5 | 1011101000 | 2e8 | OBR = 10 |
| 34 | IN R4 | 1010100000 | 2a0 | R4 = IBR |
| 35 | OUT R4 | 1011100000 | 2e0 | OBR = IBR value |
| 36 | CMP R6, R0 | 0101110000 | 170 | E = (R6 == 0) |
| 37 | BEQ 2 | 1100000010 | 302 | exit when R6 == 0 |
| 38 | ADDI R6, -1 | 0001110111 | 077 | R6 = R6 - 1 |
| 39 | JMP -4 | 1110111100 | 3bc | back to the CMP |
| 40 | HALT  | 1111000000 | 3c0 | stop |

## What each section tests

- **Addresses 0 to 8:** ADDI, ADD, SUB (negative result), AND, OR, SLL.
- **Addresses 9 to 12:** CMP then BLT taken, with a poison instruction that must be skipped.
- **Addresses 13 to 16:** CMP then BEQ taken, with a skipped poison instruction.
- **Addresses 17 to 19:** BEQ not taken. R6 only reaches 3 if the branch falls through.
- **Addresses 20 to 23:** signed compare. -3 < 1 must set L, which would fail with an unsigned compare or a raw MSB flag.
- **Addresses 24 to 25:** JMP forward.
- **Addresses 26 to 32:** R7 base register, SW and LW with offsets 0, +1, and -1.
- **Addresses 33 to 35:** OUT, IN, OUT.
- **Addresses 36 to 40:** countdown loop using CMP against R0, BEQ, ADDI -1, backward JMP, then HALT.

## Expected results

### Checkpoint 1: PC = 26 (before the memory test)

| Register | Hex | Decimal |
|---|---|---|
| R1 | 00A | 10 |
| R2 | 3FD | -3 |
| R3 | 001 | 1 |
| R4 | 007 | 7 |
| R5 | 002 | 2 |
| R6 | 003 | 3 |
| R7 | 000 | 0 |

If R5 is not 2 or R6 is not 3, one of the poison instructions ran, or a branch was taken or skipped incorrectly.

### Final state: PC stops at 40 (HALT)

| Item | Hex | Decimal | Note |
|---|---|---|---|
| R1 | 00A | 10 | |
| R2 | 3FD | -3 | |
| R3 | 3FD | -3 | loaded from Mem[2] |
| R4 | IBR value | | from IN. If the IBR holds 155, R4 = 155 |
| R5 | 00A | 10 | loaded from Mem[3] |
| R6 | 000 | 0 | loop counted 7 down to 0 |
| R7 | 003 | 3 | base address |
| OBR | IBR value | | last OUT wrote R4 |
| Mem[2] | 3FD | -3 | |
| Mem[3] | 00A | 10 | |
| Mem[4] | 007 | 7 | |

The OBR shows 00A (10) after address 33, and then the IBR value after address 35.

Set the IBR to a known value (for example 155 hex) before running. If you leave it at 0, R4 and the OBR end at 0.

The program takes 63 clock cycles from reset to HALT.

## Control signals on every clock cycle

This is a single-cycle CPU, so each clock cycle executes exactly one instruction. A row shows the control signals **during** that cycle, which is when they are stable. State changes (register write, RAM write, PC update, E and L latch, OBR load) all happen on the rising edge at the end of the cycle.

How to read the table:
- **Cycle** counts from 1 at reset. **PC** is the instruction address fetched during that cycle.
- **E** and **L** are the flag values held during the cycle, so they are the values left by the most recent CMP. A CMP updates them at the end of its own cycle, so the next instruction is the first to see the new values.
- **Branch** shows the resolved value, after combining the decoder output with E and L. BEQ shows 1 only when E = 1, and BLT shows 1 only when L = 1.
- **AluOp**, **BInvert**, and **WriteBackSrc** are direct taps of opcode bits, so they always carry a value, even for instructions that ignore them (those cases are marked `x` in the truth table in the design notes). The values below are what the wires will actually show.
- The run assumes the IBR holds a known value and that the clock keeps running until HALT. Control signals do not depend on the IBR value.
- The skipped "poison" instructions (PC 11, 15, 22, and 25) never execute, so they have no row. The PC column jumps over them.
- Checkpoint 1 (PC = 26) is cycle 23. Check the registers at the start of that cycle.
- The final HALT cycle repeats forever. The PC enable is off, so the PC stays at 40 and every signal in that row stays constant.

| Cycle | PC | Instruction | RegWrite | WriteBackSrc | R7 | Imm | AluOp | BInvert | Shift | MemWrite | CMP | Output | Branch | Halt | E | L |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | ADDI R1, 3 | 1 | 00 | 0 | 1 | 01 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2 | 1 | ADDI R2, 2 | 1 | 00 | 0 | 1 | 01 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3 | 2 | ADD R1, R2 | 1 | 00 | 0 | 0 | 00 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 4 | 3 | SUB R2, R1 | 1 | 00 | 0 | 0 | 00 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 5 | 4 | ADDI R3, 3 | 1 | 00 | 0 | 1 | 01 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 6 | 5 | AND R3, R1 | 1 | 01 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 7 | 6 | ADDI R4, 2 | 1 | 00 | 0 | 1 | 01 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 8 | 7 | OR R4, R1 | 1 | 01 | 0 | 0 | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 9 | 8 | SLL R1, R3 | 1 | 01 | 0 | 0 | 10 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 10 | 9 | CMP R3, R4 | 0 | 00 | 0 | 0 | 01 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| 11 | 10 | BLT 1 | 0 | 10 | 0 | 0 | 01 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| 12 | 12 | ADDI R5, 1 | 1 | 00 | 0 | 1 | 01 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| 13 | 13 | CMP R3, R3 | 0 | 00 | 0 | 0 | 01 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| 14 | 14 | BEQ 1 | 0 | 10 | 0 | 0 | 00 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 |
| 15 | 16 | ADDI R6, 2 | 1 | 00 | 0 | 1 | 01 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| 16 | 17 | CMP R3, R4 | 0 | 00 | 0 | 0 | 01 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 |
| 17 | 18 | BEQ 1 | 0 | 10 | 0 | 0 | 00 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| 18 | 19 | ADDI R6, 1 | 1 | 00 | 0 | 1 | 01 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| 19 | 20 | CMP R2, R3 | 0 | 00 | 0 | 0 | 01 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| 20 | 21 | BLT 1 | 0 | 10 | 0 | 0 | 01 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| 21 | 23 | ADDI R5, 1 | 1 | 00 | 0 | 1 | 01 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| 22 | 24 | JMP 1 | 0 | 11 | 0 | 0 | 10 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| 23 | 26 | ADDI R7, 3 | 1 | 00 | 0 | 1 | 01 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| 24 | 27 | SW R1, 0 | 0 | 10 | 1 | 1 | 01 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| 25 | 28 | SW R4, 1 | 0 | 10 | 1 | 1 | 01 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| 26 | 29 | SW R2, -1 | 0 | 10 | 1 | 1 | 01 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| 27 | 30 | LW R5, 0 | 1 | 10 | 1 | 1 | 00 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| 28 | 31 | LW R6, 1 | 1 | 10 | 1 | 1 | 00 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| 29 | 32 | LW R3, -1 | 1 | 10 | 1 | 1 | 00 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| 30 | 33 | OUT R5 | 0 | 11 | 0 | 0 | 11 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| 31 | 34 | IN R4 | 1 | 11 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| 32 | 35 | OUT R4 | 0 | 11 | 0 | 0 | 11 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| 33 | 36 | CMP R6, R0 | 0 | 00 | 0 | 0 | 01 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| 34 | 37 | BEQ 2 | 0 | 10 | 0 | 0 | 00 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 35 | 38 | ADDI R6, -1 | 1 | 00 | 0 | 1 | 01 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 36 | 39 | JMP -4 | 0 | 11 | 0 | 0 | 10 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| 37 | 36 | CMP R6, R0 | 0 | 00 | 0 | 0 | 01 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| 38 | 37 | BEQ 2 | 0 | 10 | 0 | 0 | 00 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 39 | 38 | ADDI R6, -1 | 1 | 00 | 0 | 1 | 01 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40 | 39 | JMP -4 | 0 | 11 | 0 | 0 | 10 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| 41 | 36 | CMP R6, R0 | 0 | 00 | 0 | 0 | 01 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| 42 | 37 | BEQ 2 | 0 | 10 | 0 | 0 | 00 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 43 | 38 | ADDI R6, -1 | 1 | 00 | 0 | 1 | 01 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 44 | 39 | JMP -4 | 0 | 11 | 0 | 0 | 10 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| 45 | 36 | CMP R6, R0 | 0 | 00 | 0 | 0 | 01 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| 46 | 37 | BEQ 2 | 0 | 10 | 0 | 0 | 00 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 47 | 38 | ADDI R6, -1 | 1 | 00 | 0 | 1 | 01 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 48 | 39 | JMP -4 | 0 | 11 | 0 | 0 | 10 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| 49 | 36 | CMP R6, R0 | 0 | 00 | 0 | 0 | 01 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| 50 | 37 | BEQ 2 | 0 | 10 | 0 | 0 | 00 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 51 | 38 | ADDI R6, -1 | 1 | 00 | 0 | 1 | 01 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 52 | 39 | JMP -4 | 0 | 11 | 0 | 0 | 10 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| 53 | 36 | CMP R6, R0 | 0 | 00 | 0 | 0 | 01 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| 54 | 37 | BEQ 2 | 0 | 10 | 0 | 0 | 00 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 55 | 38 | ADDI R6, -1 | 1 | 00 | 0 | 1 | 01 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 56 | 39 | JMP -4 | 0 | 11 | 0 | 0 | 10 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| 57 | 36 | CMP R6, R0 | 0 | 00 | 0 | 0 | 01 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| 58 | 37 | BEQ 2 | 0 | 10 | 0 | 0 | 00 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 59 | 38 | ADDI R6, -1 | 1 | 00 | 0 | 1 | 01 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 60 | 39 | JMP -4 | 0 | 11 | 0 | 0 | 10 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| 61 | 36 | CMP R6, R0 | 0 | 00 | 0 | 0 | 01 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| 62 | 37 | BEQ 2 | 0 | 10 | 0 | 0 | 00 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 |
| 63 | 40 | HALT | 0 | 11 | 0 | 0 | 11 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |

Every row can be checked against the truth table in the design notes. A quick sanity pass:
- `RegWrite` is 1 in every ADD, ADDI, AND, OR, SUB, SLL, LW, and IN row, and 0 everywhere else.
- `MemWrite` is 1 in exactly three rows (the three SW cycles), and `CMP` is 1 in exactly the CMP rows.
- `Output` is 1 in exactly two rows (the two OUT cycles).
- `Branch` is 1 only in rows where a branch or jump is actually taken, and the PC in the next row jumps accordingly.
- `Halt` is 1 in only the last row.
