import sys


# List of the instructions
instr = {   "HALT":     1,  "LOAD":     2,
            "STORE":    3,  "ADD":      4,
            "SUB":      5,  "INC":      6,
            "DEC":      7,  "XOR":      8,
            "AND":      9,  "OR":       10,
            "NOT":      11, "SHL":      12,
            "SHR":      13, "NOP":      14,
            "PUSH":     15, "POP":      16,
            "CMP":      17, "JMP":      18,
            "JZ":       19, "JE":       19,
            "JNZ":      20, "JNE":      20,
            "JC":       21, "JNC":      22,
            "JA":       23, "JAE":      24,
            "JB":       25, "JBE":      26,
            "READ":     27, "PRINT":    28}

register = {"PC":   "0000",
            'A':    "0001",
            "B":    "0002",
            "C":    "0003",
            "D":    "0004",
            "E":    "0005",
            "S":    "0006"}


loc_counter = 0
isInstr = True
addressing_mode= ""
operand=""
bits = ""
counter=0
# Opening the input file prog.asm

with open("prog.asm") as asmfile:

    for line in asmfile:
        line = line.split() # Splitting the strings into separate operands   
        value = line[0]
        opcode   = ""
        addrmode = ""
        operand  = ""

        if value in instr:          # The value is one of the instructions
            opcode = instr[value]
            isInstr = True
            print(value)
            print(counter)
            counter+=1
            


        elif value.__contains__(":"):               
            isInstr = False       
            operand = hex((counter-1) * 3)[2:]
            print(operand)
            
        else:
            isInstr = False
            print(value)

        if isInstr == True:
            
            if value == "HALT":
                addressing_mode = "00"
                operand = "00"
            else:
                if line[1][0] == "'" and line[1][-1] == "'":
                    var=line[1][1:-1].encode('utf-8')
                    operand = var.hex()
                    addressing_mode = 00
                    
                elif line[1][0] == "[" and line[1][-1] == "]":
                    var = line[1][1:-1]

                    if register.__contains__(var):
                        operand = register[var]
                        addressing_mode = "10"
                    else: 
                        addressing_mode = "11"
                
