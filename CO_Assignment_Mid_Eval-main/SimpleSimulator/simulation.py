import matplotlib.pyplot as plt
import random as rand

memory = []
for mem in range(0, 256):
    memory.append("0000000000000000")

unusedBits = "0" * 12
reg0 = 0
reg1 = 0
reg2 = 0
reg3 = 0
reg4 = 0
reg5 = 0
reg6 = 0
FLAGS = unusedBits + "0000"

# register_values = [reg0, reg1, reg2, reg3, reg4, reg5, reg6, FLAGS]
register_dict = {"000": reg0, "001": reg1, "010": reg2,
                 "011": reg3, "100": reg4, "101": reg5, "110": reg6, "111": FLAGS}
Flag_dict = {"V": "1000", "L": "100", "G": "010", "E": "001"}
register_addr = ["000", "001", "010", "011", "100", "101", "110", "111"]
op_code_dict = {"00000": ["a", "add"],
                "00001": ["a", "sub"],
                "00010": ["b", "movimm"],
                "00011": ["c", "movreg"],
                "00100": ["d", "ld"],
                "00101": ["d", "st"],
                "00110": ["a", "mul"],
                "00111": ["c", "div"],
                "01000": ["b", "rs"],
                "01001": ["b", "ls"],
                "01010": ["a", "xor"],
                "01011": ["a", "or"],
                "01100": ["a", "and"],
                "01101": ["c", "not"],
                "01110": ["c", "cmp"],
                "01111": ["e", "jmp"],
                "10000": ["e", "jlt"],
                "10001": ["e", "jgt"],
                "10010": ["e", "je"],
                "10011": ["f", "hlt"],
                }


def simulator(instruction):
    opcode = instruction[0: 5]
    type = op_code_dict[opcode][0]
    temp_flag = register_dict["111"]
    register_dict["111"] = "0000000000000000"

    if (type == "a"):
        reg1_value = register_dict[instruction[7:10]]
        reg2_value = register_dict[instruction[10:13]]
        reg3_value = register_dict[instruction[13:]]

        if opcode == "00000":  # addition   # overflow pending
            check = reg2_value + reg3_value
            if (check < 0 or check > 255):
                register_dict["111"] = register_dict["111"][0:12] + \
                    "1"+register_dict["111"][13:]
                check_1 = convert(check)
                new_value = check_1[-16:]
                register_dict[instruction[7:10]] = int(new_value, 2)

            else:
                register_dict[instruction[7:10]] = check

        if opcode == "00001":  # substraction   # overflow pending
            check = reg2_value - reg3_value
            if (check < 0 or check > 255):
                register_dict["111"] = register_dict["111"][0:12] + \
                    "1"+register_dict["111"][13:]
                register_dict[instruction[7:10]] = 0
            else:
                register_dict[instruction[7:10]] = check

        if opcode == "00110":  # multiply   # overflow pending
            check = reg2_value * reg3_value
            if (check < 0 or check > 255):
                register_dict["111"] = register_dict["111"][0:12] + \
                    "1"+register_dict["111"][13:]
                check_1 = convert(check)
                new_value = check_1[-16:]
                register_dict[instruction[7:10]] = int(new_value, 2)

            else:
                register_dict[instruction[7:10]] = check

        if opcode == "01010":  # exclusive or
            register_dict[instruction[7:10]] = int(
                bin(reg2_value ^ reg3_value), 2)
        if opcode == "01011":  # or
            register_dict[instruction[7:10]] = int(
                bin(reg2_value | reg3_value), 2)
        if opcode == "01100":  # and
            register_dict[instruction[7:10]] = int(
                bin(reg2_value & reg3_value), 2)
