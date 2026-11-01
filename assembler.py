
# ==========================================
#         10-BIT CPU ASSEMBLER
# ==========================================

#Define all 16 opcodes

OPCODES = {
    "ADD":  "0000",
    "SUB":  "0001",
    "AND":  "0010",
    "OR":   "0011",
    "XOR":  "0100",
    "SLL":  "0101",
    "SRL":  "0110",
    "LW":   "0111",
    "SW":   "1000",
    "LDI":  "1001",
    "ADDI": "1010",
    "CMP":  "1011",
    "BEQ":  "1100",
    "BLT":  "1101",
    "JMP":  "1110",
    "IO":   "1111"
}


# Define instruction formats

FORMATS = {
    "ADD": "R",
    "SUB": "R",
    "AND": "R",
    "OR":  "R",
    "XOR": "R",
    "SLL": "R",
    "SRL": "R",
    "LW":  "R",
    "SW":  "R",
    "CMP": "R",

    "LDI":  "I",
    "ADDI": "I",
    "IO":   "I",

    "BEQ": "B",
    "BLT": "B",
    "JMP": "B"
}

REGISTERS = {
    "R0": "000",
    "R1": "001",
    "R2": "010",
    "R3": "011",
    "R4": "100",
    "R5": "101",
    "R6": "110",
    "R7": "111"
}

def encode_r_type(instruction, rd, rs):

    opcode = OPCODES[instruction]
    rd_binary = REGISTERS[rd]
    rs_binary = REGISTERS[rs]

    machine_code = opcode + rd_binary + rs_binary

    return machine_code

def encode_i_type(instruction, rd, immediate):

    opcode = OPCODES[instruction]
    rd_binary = REGISTERS[rd]

    # Validate immediate values
    if instruction == "LDI":
        if immediate < 0 or immediate > 7:
            raise ValueError("LDI immediate must be between 0 and 7")

    elif instruction == "ADDI":
        if immediate < -4 or immediate > 3:
            raise ValueError("ADDI immediate must be between -4 and 3")

    elif instruction == "IO":
        if immediate not in [0, 1]:
            raise ValueError("IO immediate must be 0 or 1")

    else:
        raise ValueError("Invalid I-type instruction")

    # Convert immediate into 3-bit binary
    immediate_binary = format(immediate & 0b111, "03b")

    machine_code = opcode + rd_binary + immediate_binary

    return machine_code

def encode_b_type(instruction, offset):

    opcode = OPCODES[instruction]

    if instruction not in ["BEQ", "BLT", "JMP"]:
        raise ValueError("Invalid branch/jump instruction")

    if offset < -32 or offset > 31:
        raise ValueError("Offset must be between -32 and +31")

    offset_binary = format(offset & 0b111111, "06b")

    machine_code = opcode + offset_binary

    return machine_code

def assemble_line(line):

    # Remove comments and extra spaces
    line = line.split("#")[0].strip()

    if not line:
        return None

    # Separate instruction and operands
    parts = line.replace(",", " ").split()

    instruction = parts[0].upper()
    operands = parts[1:]

    if instruction not in OPCODES:
        raise ValueError("Unknown instruction: " + instruction)

    fmt = FORMATS[instruction]

    if fmt == "R":

        if len(operands) != 2:
            raise ValueError("R-type needs two registers")

        rd, rs = operands

        if rd not in REGISTERS or rs not in REGISTERS:
            raise ValueError("Invalid register")

        binary = encode_r_type(instruction, rd, rs)

    elif fmt == "I":

        if len(operands) != 2:
            raise ValueError("I-type needs a register and immediate")

        rd, immediate = operands

        if rd not in REGISTERS:
            raise ValueError("Invalid register")

        binary = encode_i_type(
            instruction, rd, int(immediate)
        )

    elif fmt == "B":

        if len(operands) != 1:
            raise ValueError("Branch/jump needs one offset")

        binary = encode_b_type(
            instruction, int(operands[0])
        )

    if len(binary) != 10:
        raise ValueError("Instruction is not 10 bits")

    return binary

print("\nStarting Assembler...\n")

machine_codes = []
errors = []

with open("program.asm", "r") as file:

    lines = file.readlines()

for line_number, line in enumerate(lines, start=1):

    try:
        binary = assemble_line(line)

        if binary is not None:

            hexadecimal = format(int(binary, 2), "03X")

            machine_codes.append(hexadecimal)

            print(
                f"Line {line_number}: "
                f"{binary} -> {hexadecimal}"
            )

    except ValueError as error:

        errors.append(
            f"Line {line_number}: {error}"
        )

if errors:

    print("\nAssembly Failed!")

    for error in errors:
        print(error)

else:

    with open("machine_code.txt", "w") as file:

        for code in machine_codes:
            file.write(code + "\n")

    print("\nAssembly Successful!")
    print("Total instructions:", len(machine_codes))
    print("Output saved in machine_code.txt")