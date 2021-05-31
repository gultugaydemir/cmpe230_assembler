import sys
import re

# List of the instructions
instr = {   "HALT":     "1",    "LOAD":     "2",    "STORE":    "3",    "ADD":      "4",
            "SUB":      "5",    "INC":      "6",    "DEC":      "7",    "XOR":      "8",
            "AND":      "9",    "OR":       "a",    "NOT":      "b",    "SHL":      "c",
            "SHR":      "d",    "NOP":      "e",    "PUSH":     "f",    "POP":      "10",
            "CMP":      "11",   "JMP":      "12",   "JZ":       "13",   "JE":       "13",
            "JNZ":      "14",   "JNE":      "14",   "JC":       "15",   "JNC":      "16",
            "JA":       "17",   "JAE":      "18",   "JB":       "19",   "JBE":      "1a",
            "READ":     "1b",   "PRINT":    "1c"}

register = {'A':    "0001", 'B':    "0002", "C":    "0003",
            "D":    "0004", "E":    "0005", "S":    "0006"}

label = {}

loc_counter = 0
isInstr = True
addressing_mode= ""
operand=""
bits = ""
counter=0

binFile = open("progss.bin", "w")

with open("prog.asm") as asm:
    for line in asm:
            line = line.split()
            value = line[0]
            opcode   = ""
            addrmode = ""
            operand  = ""
        
            if value.__contains__(":"):               # Is label
                operand = hex((counter) * 3)[2:]
                value=value.replace(":", "")
                label[value] = operand
            else:
                counter+=1


with open("prog.asm") as asmFile:
    for line in asmFile:
        line = line.split() 
        value = line[0]
        opcode   = ""
        addrmode = ""
        operand  = ""

        if value in instr:          
            opcode = instr[value]
            isInstr = True                          # Is instruction
        else:
            isInstr = False

        if isInstr == True:
            if value == "HALT":
                addressing_mode = "0"
                operand = "00"
            else:
                if (re.match("\'(\w)\'", line[1]) != None):         # 'A'
                    var=line[1][1:-1].encode('utf-8')
                    operand = var.hex()
                    addressing_mode = "0"
                    
                elif (re.match("\[(\w)\]", line[1]) != None):       # [A]
                    var = line[1][1:-1]
                    if register.__contains__(var):  
                        operand = register[var]
                        addressing_mode = "2"
                    else:                       
                        addressing_mode = "3"
                elif (re.match("^[ABCDES]$", line[1]) != None):     # A
                    var = line[1]
                    operand = register[var]
                    addressing_mode = "1"
                elif label.__contains__(line[1]):
                    var = label[line[1]]
                    addressing_mode = "0"
                    operand = var
                else: 
                    operand = line[1]
                    addressing_mode = "0"

        if isInstr is True:
            opcode = int(str(opcode),16) 
            addressing_mode = int(str(addressing_mode),16)             
            operand  = int(str(operand),16) 

            bopcode = format(opcode, '06b')
            baddressing_mode = format(addressing_mode, '02b')
            boperand = format(operand, '016b') 

            bin = '0b' + bopcode + baddressing_mode + boperand 
            ibin = int(bin[2:],2) ; 
            result = format(ibin, '06x')
            print(result)
            binFile.write(result+"\n")          