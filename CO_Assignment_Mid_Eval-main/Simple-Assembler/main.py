from sys import exit
from sys import stdin

halt_called = False
non_var_called = False
unusedBits = "000000000000"
inside_label = False

reg0 = 0
reg1 = 0
reg2 = 0
reg3 = 0
reg4 = 0
reg5 = 0
reg6 = 0
FLAGS = unusedBits + "0000"


register_dist = {"R0": 0, "R1": 1, "R2": 2,
                 "R3": 3, "R4": 4, "R5": 5, "R6": 6, "FLAGS": 7}
registers = [reg0, reg1, reg2, reg3, reg4, reg5, reg6, FLAGS]
register_addr = ["000", "001", "010", "011", "100", "101", "110", "111"]

list_of_instructions = ["add", "sub", "mul",
                        "div", "mov", "ld", "st", "rs", "ls", "xor", "or", "and", "not", "cmp", "jmp", "jlt", "jgt", "je", "hlt"]

variables = {}

labels = {}

Flag_dict = {"V": "1000", "L": "0100", "G": "0010", "E": "0001"}

errors = {1: "Typos in instruction name or register name",
          2: "Use of undefined variables",
          3: "Use of undefined labels",
          4: "Illegal use of FLAGS register",
          5: "Illegal Immediate values (less than 0 or more than 255)",
          6: "Misuse of labels as variables or vice-versa",
          7: "Variables not declared at the beginning",
          8: "Missing hlt instruction",
          9: "hlt not being used as the last instruction",
          10: "Wrong syntax used for instructions"}


def assembler(instruction):
    instruction = instruction.strip()
    inst = instruction.split()

    global halt_called
    global non_var_called
    if (halt_called == True):
        raiseError(9)

    if (inst[0] == "xor"):
        if ("FLAGS" in inst):
            raiseError(4)
        TypeA(inst)
        non_var_called = True
        getXOR(inst[1], inst[2], inst[3])

    elif (inst[0] == "or"):
        if ("FLAGS" in inst):
            raiseError(4)
        TypeA(inst)
        non_var_called = True
        getOR(inst[1], inst[2], inst[3])

    elif (inst[0] == "and"):
        if ("FLAGS" in inst):
            raiseError(4)
        TypeA(inst)
        non_var_called = True
        getAND(inst[1], inst[2], inst[3])

    elif (inst[0] == "not"):
        if ("FLAGS" in inst):
            raiseError(4)
        TypeC(inst)
        non_var_called = True
        getINVERT(inst[1], inst[2])

    elif (inst[0] == "rs"):
        if ("FLAGS" in inst):
            raiseError(4)
        TypeB(inst)
        inst[2] = inst[2].replace("$", "")
        if (int(inst[2]) < 0 or int(inst[2]) > 255):
            raiseError(5)
        non_var_called = True
        shiftRIGHT(inst[1], int(inst[2]))

    elif (inst[0] == "ls"):
        if ("FLAGS" in inst):
            raiseError(4)
        TypeB(inst)
        inst[2] = inst[2].replace("$", "")
        if (int(inst[2]) < 0 or int(inst[2]) > 255):
            raiseError(5)
        non_var_called = True
        shiftLEFT(inst[1], int(inst[2]))

    elif (inst[0] == "add"):
        if ("FLAGS" in inst):
            raiseError(4)
        TypeA(inst)
        non_var_called = True
        add(inst[1], inst[2], inst[3])

    elif (inst[0] == "div"):
        if ("FLAGS" in inst):
            raiseError(4)
        TypeC(inst)
        non_var_called = True
        div(inst[1], inst[2])

    elif (inst[0] == "sub"):
        if ("FLAGS" in inst):
            raiseError(4)
        TypeA(inst)
        non_var_called = True
        sub(inst[1], inst[2], inst[3])

    elif (inst[0] == "mul"):
        if ("FLAGS" in inst):
            raiseError(4)
        TypeA(inst)
        non_var_called = True
        mul(inst[1], inst[2], inst[3])

    elif (inst[0] == "mov"):
        if ("$" in inst[2]):
            TypeB(inst)
            inst[2] = inst[2].replace("$", "")
            if (int(inst[2]) < 0 or int(inst[2]) > 255):
                raiseError(5)
            non_var_called = True
            movImm(inst[1], int(inst[2]))
        else:
            TypeC(inst)
            non_var_called = True
            movReg(inst[1], inst[2])

    elif (inst[0] == "ld"):
        if ("FLAGS" in inst):
            raiseError(4)
        if (inst[2] in labels):
            raiseError(6)
        if (inst[2] not in variables):
            raiseError(2)
        TypeD(inst)
        non_var_called = True
        load(inst[1], inst[2])

    elif (inst[0] == "st"):
        if ("FLAGS" in inst):
            raiseError(4)
        if (inst[2] in labels):
            raiseError(6)
        if (inst[2] not in variables):
            raiseError(2)
        TypeD(inst)
        non_var_called = True
        store(inst[1], inst[2])

    elif (inst[0] == "cmp"):
        if ("FLAGS" in inst):
            raiseError(4)
        TypeC(inst)
        non_var_called = True
        compare(inst[1], inst[2])

    elif (inst[0] == "jmp"):
        if (inst[1] in variables):
            raiseError(6)
        if (inst[1] not in labels):
            raiseError(3)
        non_var_called = True
        unconditionalJump(inst[1])

    elif (inst[0] == "jlt"):
        if (inst[1] in variables):
            raiseError(6)
        if (inst[1] not in labels):
            raiseError(3)
        non_var_called = True
        jumplt(inst[1])

    elif (inst[0] == "jgt"):
        if (inst[1] in variables):
            raiseError(6)
        if (inst[1] not in labels):
            raiseError(3)
        non_var_called = True
        jumpgt(inst[1])

    elif (inst[0] == "je"):
        if (inst[1] in variables):
            raiseError(6)
        if (inst[1] not in labels):
            raiseError(3)
        non_var_called = True
        jumpeq(inst[1])

    elif (inst[0] == "hlt"):
        TypeF(inst)
        halt_called = True
        halt()

    elif (inst[0] == "var"):
        if (non_var_called == True):
            raiseError(7)
        if (inst[1] in list_of_instructions):
            raiseError(10)
        global count
        variables[inst[1]] = str(format(count, '08b'))
        count += 1

    elif (":" in inst[0]):
        global inside_label
        if (inside_label == True):
            raiseError(10)
        if (inst[0] in list_of_instructions):
            raiseError(10)
        inst[0] = inst[0].replace(":", "")
        labels[inst[0]] = str(format(program_counter, '08b'))
        non_var_called = True
        if (len(inst) > 1):
            sub_inst = " ".join(inst[1:])
            inside_label = True
            assembler(sub_inst)
            inside_label = False

    else:
        raiseError(1)


def load(r1, mem_add):
    opCode = "00100"
    regBits = register_addr[register_dist[r1]]
    memBits = variables[mem_add]
    print(opCode + regBits + str(memBits) + "\n")


def store(r1, mem_add):
    opCode = "00101"
    regBits = register_addr[register_dist[r1]]
    memBits = variables[mem_add]
    print(opCode + regBits + str(memBits) + "\n")


def unconditionalJump(mem_add):
    global program_counter
    opCode = "01111"
    exBits = "000"
    memBits = format(program_counter, '08b')
    program_counter = labels[mem_add] - 1
    print(opCode + exBits + str(memBits) + "\n")


def jumplt(mem_add):
    global program_counter
    opCode = "10000"
    exBits = "000"
    memBits = format(program_counter, '08b')

    program_counter = labels[mem_add] - 1
    print(opCode + exBits + str(memBits) + "\n")


def jumpgt(mem_add):
    global program_counter
    opCode = "10001"
    exBits = "000"
    memBits = format(program_counter, '08b')

    program_counter = labels[mem_add] - 1
    print(opCode + exBits + str(memBits) + "\n")


def jumpeq(mem_add):
    global program_counter
    opCode = "10010"
    exBits = "000"
    memBits = format(program_counter, '08b')

    program_counter = labels[mem_add] - 1
    print(opCode + exBits + str(memBits) + "\n")
