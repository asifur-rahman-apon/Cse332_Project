import sys
OPCODES = {
    "ADD":  "0000",
    "SUB":  "0001",
    "AND":  "0010",
    "OR":   "0011",
    "SLL":  "0100",
    "CMP":  "0101",
    "ADDI": "0110",
    "LW":   "1000",
    "SW":   "1001",
    "IN":   "1010",
    "OUT":  "1011",
    "BEQ":  "1100",
    "BLT":  "1101",
    "JMP":  "1110",
    "HALT": "1111"
}



FORMATS = {
    "ADD": "R",
    "SUB": "R",
    "AND": "R",
    "OR":  "R",
    "SLL": "R",
    "CMP": "R",

    "ADDI": "I",
    "LW":   "I",
    "SW":   "I",

    "IN":  "R1",
    "OUT": "R1",

    "BEQ": "B",
    "BLT": "B",
    "JMP": "B",

    "HALT": "N"
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


def encode_r1_type(instruction, rd):

    # IN / OUT: only Rd is used, Rs field is unused (000)
    opcode = OPCODES[instruction]
    rd_binary = REGISTERS[rd]

    machine_code = opcode + rd_binary + "000"

    return machine_code

def encode_n_type(instruction):

    # HALT: no operands, bits 5:0 are don't-care (000000)
    opcode = OPCODES[instruction]

    machine_code = opcode + "000000"

    return machine_code

def encode_i_type(instruction, rd, immediate):

    opcode = OPCODES[instruction]
    rd_binary = REGISTERS[rd]

    
    if instruction in ["ADDI", "LW", "SW"]:
        if immediate < -4 or immediate > 3:
            raise ValueError(instruction + " immediate must be between -4 and 3")

    
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

def first_pass(lines, errors):

    # pass 1: find address of every label

    labels = {} # maps labels with their addresses
    addresses = {} # maps line numbers in the original file to an actual address
    address = 0 #keeps track of how many actual addresses we have gone through

    for line_number, line in enumerate(lines, start=1):

        # remove comments starting with # 
        line = line.split("#")[0].strip().upper()

        # remove label, validate label and store label with its address (current value of address)
        while ":" in line:

            label, line = line.split(":", 1)
            label = label.strip()
            line = line.strip()

            if not label.isidentifier():
                errors.append(
                    f"Line {line_number}: Invalid label: '{label}'"
                )
            elif label.upper() in REGISTERS or label.upper() in OPCODES:
                errors.append(
                    f"Line {line_number}: Label '{label}' clashes with a register/instruction name"
                )
            elif label in labels:
                errors.append(
                    f"Line {line_number}: Duplicate label: '{label}'"
                )
            else:
                labels[label] = address # new label found, store with address of current line

        # if a line was not removed, it is an instruction so give it an address and increment address
        if line:
            addresses[line_number] = address 
            address += 1

    return labels, addresses

def assemble_line(line, address, labels):

    
    line = line.split("#")[0].strip().upper()

    # drop any "label:" prefix (labels were already recorded in pass 1)
    line = line.rsplit(":", 1)[-1].strip()

    # if nothing remains, return 
    if not line:
        return None

    
    parts = line.replace(",", " ").split()

    instruction = parts[0]
    operands = parts[1:]

    if instruction not in OPCODES:
        raise ValueError("Unknown instruction: " + instruction)

    fmt = FORMATS[instruction] # set format of current instruction

    if fmt == "R":

        if len(operands) != 2:
            raise ValueError("R-type needs two registers")

        rd, rs = operands

        if rd not in REGISTERS or rs not in REGISTERS:
            raise ValueError("Invalid register")

        binary = encode_r_type(instruction, rd, rs)

    elif fmt == "R1":

        if len(operands) != 1:
            raise ValueError(instruction + " needs one register")

        rd = operands[0]

        if rd not in REGISTERS:
            raise ValueError("Invalid register")

        binary = encode_r1_type(instruction, rd)

    elif fmt == "N":

        if len(operands) != 0:
            raise ValueError(instruction + " takes no operands")

        binary = encode_n_type(instruction)

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
            raise ValueError("Branch/jump needs one offset or label")

        target = operands[0]

        if target in labels:
            # PC-relative: target = (branch address + 1) + offset
            offset = labels[target] - (address + 1)
        else:
            try:
                offset = int(target) # interpret target as an immediate offset
            except ValueError:
                raise ValueError("Undefined label: " + target)

        binary = encode_b_type(
            instruction, offset
        )

    if len(binary) != 10:
        raise ValueError("Instruction is not 10 bits")

    return binary

print("\nStarting Assembler...\n")

machine_codes = []
errors = []

if len(sys.argv) > 1:
    input_file = sys.argv[1].strip()
else:
    user_input = input("Enter assembly filename (default: program.asm): ").strip()
    input_file = user_input if user_input else "program.asm"

try:
    with open(input_file, "r") as file:
        lines = file.readlines()
except FileNotFoundError:
    print(f"Error: Input file '{input_file}' not found.")
    sys.exit(1)

labels, addresses = first_pass(lines, errors)


for line_number, line in enumerate(lines, start=1):

    try:
        binary = assemble_line(line, addresses.get(line_number), labels)

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
