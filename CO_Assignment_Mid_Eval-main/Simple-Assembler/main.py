from sys import exit
from sys import stdin

halt_called = False
non_var_called = False
unusedBits = "000000000000"
inside_label = False
inside_jump = False

reg0 = 0
reg1 = 0
reg2 = 0
reg3 = 0
reg4 = 0
reg5 = 0
reg6 = 0
FLAGS = unusedBits + "0000"


register_dict = {"R0": 0, "R1": 1, "R2": 2,
                 "R3": 3, "R4": 4, "R5": 5, "R6": 6, "FLAGS": 7}
registers = [reg0, reg1, reg2, reg3, reg4, reg5, reg6, FLAGS]
register_addr = ["000", "001", "010", "011", "100", "101", "110", "111"]

list_of_instructions = ["add", "sub", "mul",
                        "div", "mov", "ld", "st", "rs", "ls", "xor", "or", "and", "not", "cmp", "jmp", "jlt", "jgt", "je", "hlt"]

variables = {}
variables_values = {}

labels = {}

Flag_dict = {"V": "1000", "L": "100", "G": "010", "E": "001"}

errors = {1: "Typos in instruction name or register name",
          2: "Use of undefined variables",
          3: "Use of undefined labels",
          4: "Illegal use of FLAGS register",
          5: "Illegal Immediate values (less than 0 or more than 255)",
          6: "Misuse of labels as variables or vice-versa",
          7: "Variables not declared at the beginning",
          8: "Missing hlt instruction",
          9: "hlt not being used as the last instruction",
          10: "Wrong syntax used for instructions",
          11: "General Syntax Error"}

temp_flag = ""


def assembler(instruction):
    instruction = instruction.strip()
    inst = instruction.split()
    global temp_flag
    temp_flag = registers[7]
    registers[7] = "0000000000000000"

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
            raiseError(11)
        global count
        variables[inst[1]] = str(format(count, '08b'))
        variables_values[inst[1]] = 0
        count += 1

    elif (":" in inst[0]):
        global inside_label
        if (inside_label == True):
            raiseError(11)
        label_name = inst[0].replace(":", "")
        if (label_name in list_of_instructions):
            raiseError(11)

        non_var_called = True
        if (len(inst) > 1):
            sub_inst = " ".join(inst[1:])
            inside_label = True
            assembler(sub_inst)
            inside_label = False

    else:
        raiseError(1)
        
        
def getAND(r1, r2, r3):
    opCode = "01100"
    exBits = "00"
    list1 = [r1, r2, r3]
    list2 = []

    for i in (list1):
        index = register_dict[i]
        list2.append(index)

    #Calculation Part#
    if (inside_jump == False):
        registers[list2[0]] = registers[list2[1]] & registers[list2[2]]  # int(
        # bin(registers[list2[1]]) & bin(registers[list2[2]]), 2)

    #printing part#
    final_bin = register_addr[list2[0]] + \
        register_addr[list2[1]] + register_addr[list2[2]]
    print(opCode + exBits + final_bin + "\n")


def getOR(r1, r2, r3):
    opCode = "01011"
    exBits = "00"
    list1 = [r1, r2, r3]
    list2 = []

    for i in (list1):
        index = register_dict[i]
        list2.append(index)

    #Calculation Part#
    if (inside_jump == False):
        registers[list2[0]] = (registers[list2[1]] | registers[list2[2]])

    #printing part#
    final_bin = register_addr[list2[0]] + \
        register_addr[list2[1]] + register_addr[list2[2]]
    print(opCode + exBits + final_bin + "\n")


def getXOR(r1, r2, r3):
    opCode = "01010"
    exBits = "00"
    list1 = [r1, r2, r3]
    list2 = []

    for i in (list1):
        index = register_dict[i]
        list2.append(index)

    #Calculation Part#
    if (inside_jump == False):
        registers[list2[0]] = (registers[list2[1]] ^ registers[list2[2]])

    #printing part#
    final_bin = register_addr[list2[0]] + \
        register_addr[list2[1]] + register_addr[list2[2]]
    print(opCode + exBits + final_bin + "\n")


def shiftRIGHT(r1, imm):
    opCode = "01000"
    index = register_dict[r1]
    regCode = register_addr[index]
    immCode = format(imm, '08b')
    print(opCode + regCode + immCode + "\n")
    if (inside_jump == False):
        registers[index] = registers[index] >> imm


def shiftLEFT(r1, imm):
    opCode = "01001"
    index = register_dict[r1]
    regCode = register_addr[index]
    immCode = format(imm, '08b')
    print(opCode + regCode + immCode + "\n")
    if (inside_jump == False):
        registers[index] = registers[index] << imm


def halt():
    opCode = "10011"
    exBits = "0"*11
    print(opCode + exBits + "\n")


def getINVERT(r1, r2):
    opCode = "01101"
    exBits = "00000"
    list1 = [r1, r2]
    list2 = []

    for i in (list1):
        index = register_dict[i]
        list2.append(index)

    #Calculation Part#
    if (inside_jump == False):
        binary_string = format(registers[list2[1]], 'b').zfill(
            16)    # correct this
        for i in range(len(binary_string)):
            if (i == len(binary_string) - 1):
                if (binary_string[i] == "0"):
                    binary_string = binary_string[0:-1] + "1"
                else:
                    binary_string = binary_string[0:-1] + "0"
            elif (binary_string[i] == "0"):
                binary_string = binary_string[0:i] + "1" + binary_string[i+1:]
            else:
                binary_string = binary_string[0:i] + "0" + binary_string[i+1:]

        value = int(binary_string, 2)
        registers[list2[0]] = value
    #printing part#

    final_bin = register_addr[list2[0]] + register_addr[list2[1]]
    print(opCode + exBits + final_bin + "\n")


def load(r1, mem_add):
    opCode = "00100"
    regBits = register_addr[register_dict[r1]]
    memBits = variables[mem_add]
    if (inside_jump == False):
        registers[register_dict[r1]] = (
            variables_values[mem_add])  # checkkkkkk
    print(opCode + regBits + str(memBits) + "\n")


def store(r1, mem_add):
    opCode = "00101"
    regBits = register_addr[register_dict[r1]]
    memBits = variables[mem_add]
    if (inside_jump == False):
        variables_values[mem_add] = registers[register_dict[r1]]
    print(opCode + regBits + str(memBits) + "\n")


def unconditionalJump(mem_add):
    global program_counter
    global inside_jump
    opCode = "01111"
    exBits = "000"
    memBits = format(labels[mem_add], '08b')
    if (inside_jump == False):
        temp_program_counter = program_counter + 1
        program_counter = labels[mem_add]

        while (temp_program_counter < program_counter):
            inside_jump = True
            assembler(content[temp_program_counter])
            temp_program_counter += 1
        inside_jump = False
    print(opCode + exBits + str(memBits) + "\n")


def jumplt(mem_add):
    global program_counter
    global temp_flag
    global inside_jump
    opCode = "10000"
    exBits = "000"
    memBits = format(labels[mem_add], '08b')
    if (inside_jump == False):
        if (temp_flag == "0000000000000100" or temp_flag == "0000000000001100"):
            temp_program_counter = program_counter + 1
            program_counter = labels[mem_add]
            while (temp_program_counter < program_counter):
                inside_jump = True
                assembler(content[temp_program_counter])
                temp_program_counter += 1
            inside_jump = False
    print(opCode + exBits + str(memBits) + "\n")


def jumpgt(mem_add):
    global program_counter
    global temp_flag
    global inside_jump
    opCode = "10001"
    exBits = "000"
    memBits = format(labels[mem_add], '08b')
    if (inside_jump == False):
        if (temp_flag == "0000000000000010" or temp_flag == "0000000000001010"):
            temp_program_counter = program_counter + 1
            program_counter = labels[mem_add]
            while (temp_program_counter < program_counter):
                inside_jump = True
                assembler(content[temp_program_counter])
                temp_program_counter += 1
            inside_jump = False
    print(opCode + exBits + str(memBits) + "\n")


def jumpeq(mem_add):
    global program_counter
    global temp_flag
    global inside_jump
    opCode = "10010"
    exBits = "000"
    memBits = format(labels[mem_add], '08b')
    if (inside_jump == False):
        if (temp_flag == "0000000000000001" or temp_flag == "0000000000001001"):
            temp_program_counter = program_counter + 1
            program_counter = labels[mem_add]
            while (temp_program_counter < program_counter):
                inside_jump = True
                assembler(content[temp_program_counter])
                temp_program_counter += 1
            inside_jump = False
    print(opCode + exBits + str(memBits) + "\n")
    
    
def add(r1, r2, r3):
    opCode = "00000"
    exBits = "00"
    list1 = [r1, r2, r3]
    list2 = []

    for i in (list1):
        index = register_dict[i]
        list2.append(index)

    #Calculation Part#
    if (inside_jump == False):
        temp = registers[list2[1]] + \
            registers[list2[2]]

        if (temp >= 0 and temp <= (2 ** 16)-1):
            registers[list2[0]] = temp
        else:
            # global FLAGS
            registers[7] = registers[7][0:12]+"1"+registers[7][13:]

    final_bin = register_addr[list2[0]] + \
        register_addr[list2[1]] + register_addr[list2[2]]
    print(opCode + exBits + final_bin + "\n")


def sub(r1, r2, r3):
    opCode = "00001"
    exBits = "00"
    list1 = [r1, r2, r3]
    list2 = []

    for i in (list1):
        index = register_dict[i]
        list2.append(index)

    #Calculation Part#
    if (inside_jump == False):
        temp = registers[list2[1]] - \
            registers[list2[2]]
        if (temp >= 0 and temp <= (2 ** 16)-1):
            registers[list2[0]] = temp
        else:
            registers[list2[0]] = 0
            # global FLAGS
            registers[7] = registers[7][0:12]+"1"+registers[7][13:]

    #printing part#
    final_bin = register_addr[list2[0]] + \
        register_addr[list2[1]] + register_addr[list2[2]]
    print(opCode + exBits + final_bin + "\n")


def mul(r1, r2, r3):
    opCode = "00110"
    exBits = "00"
    list1 = [r1, r2, r3]
    list2 = []

    for i in (list1):
        index = register_dict[i]
        list2.append(index)

    if (inside_jump == False):
        temp = registers[list2[1]] * \
            registers[list2[2]]
        if (temp >= 0 and temp <= (2 ** 16)-1):
            registers[list2[0]] = temp
        else:
            registers[7] = registers[7][0:12]+"1"+registers[7][13:]

    #printing part#
    final_bin = register_addr[list2[0]] + \
        register_addr[list2[1]] + register_addr[list2[2]]
    print(opCode + exBits + final_bin + "\n")


def div(r3, r4):
    opCode = "00111"
    exBits = "00000"
    list1 = [r3, r4]
    list2 = []

    for i in (list1):
        index = register_dict[i]
        list2.append(index)

    #Calculation Part#
    if (inside_jump == False):
        registers[0] = registers[list2[0]] / registers[list2[1]]
        registers[1] = registers[list2[0]] % registers[list2[1]]

    #printing part#
    final_bin = register_addr[list2[0]] + \
        register_addr[list2[1]]
    print(opCode + exBits + final_bin + "\n")


def movImm(r1, imm):
    opCode = "00010"

    index = register_dict[r1]
    regBits = register_addr[index]
    immCode = format(imm, '08b')

    if (inside_jump == False):
        registers[index] = imm

    print(opCode + regBits + immCode + "\n")


def movReg(r1, r2):
    opCode = "00011"
    exBits = "00000"
    list1 = [r1, r2]
    list2 = []

    for i in (list1):
        index = register_dict[i]
        list2.append(index)

    #Calculation Part#
    if (inside_jump == False):
        if (r2 == "FLAGS"):
            registers[list2[0]] = int(temp_flag, 2)
        else:
            # checkkkkkkk for flags register
            registers[list2[0]] = registers[list2[1]]

    #printing part#
    final_bin = register_addr[list2[0]] + register_addr[list2[1]]
    print(opCode + exBits + final_bin + "\n")


def compare(r1, r2):
    opCode = "01110"
    exBits = "00000"
    regBits = register_addr[register_dict[r1]] + \
        register_addr[register_dict[r2]]
    print(opCode + exBits + regBits + "\n")  # checkkkkkkkkkkkkkkk
    if (inside_jump == False):
        if (registers[register_dict[r1]] > registers[register_dict[r2]]):
            registers[7] = registers[7][0:13] + Flag_dict["G"]
        if (registers[register_dict[r1]] < registers[register_dict[r2]]):
            registers[7] = registers[7][0:13] + Flag_dict["L"]
        if (registers[register_dict[r1]] == registers[register_dict[r2]]):
            registers[7] = registers[7][0:13] + Flag_dict["E"]


def TypeA(inst):
    if ("r" in inst[1:]):
        raiseError(1)

    for i in inst[1:]:
        s = i.replace("R", "")
        if (s.isnumeric()):
            if (int(s) < 0 or int(s) > 6):
                raiseError(1)

    if (len(inst) == 4 and inst[1] in register_dict.keys() and inst[2] in register_dict.keys() and inst[3] in register_dict.keys()):
        return
    else:
        raiseError(10)


def TypeB(instr):
    if ("r" in instr[1]):
        raiseError(1)
    s = instr[1].replace("R", "")
    if (s.isnumeric()):
        if (int(s) < 0 or int(s) > 6):
            raiseError(1)

    ins = instr[2].replace("$", "")
    if (len(instr) == 3 and instr[1] in register_dict.keys() and "$" in instr[2] and ins.isnumeric()):
        return
    else:
        raiseError(10)


def TypeC(inst):
    if ("r" in inst):
        raiseError(1)

    for i in inst[1:]:
        s = i.replace("R", "")
        if (s.isnumeric()):
            if (int(s) < 0 or int(s) > 6):
                raiseError(1)
        if (s.isalpha()):
            if (s != "FLAGS"):
                raiseError(1)

    if (len(inst) == 3 and inst[1] in register_dict.keys() and inst[2] in register_dict.keys()):
        return
    else:
        raiseError(10)


def TypeD(inst):
    if ("r" in inst[1]):
        raiseError(1)
    s = inst[1].replace("R", "")
    if (s.isnumeric()):
        if (int(s) < 0 or int(s) > 6):
            raiseError(1)

    if (len(inst) == 3 and inst[1] in register_dict.keys() and inst[2] in variables):
        return
    else:
        raiseError(10)
    
    
