import sys
import re

# Dict for the instructions and the opcodes
instr = {   "HALT":     "1",    "LOAD":     "2",    "STORE":    "3",    "ADD":      "4",
            "SUB":      "5",    "INC":      "6",    "DEC":      "7",    "XOR":      "8",
            "AND":      "9",    "OR":       "a",    "NOT":      "b",    "SHL":      "c",
            "SHR":      "d",    "NOP":      "e",    "PUSH":     "f",    "POP":      "10",
            "CMP":      "11",   "JMP":      "12",   "JZ":       "13",   "JE":       "13",
            "JNZ":      "14",   "JNE":      "14",   "JC":       "15",   "JNC":      "16",
            "JA":       "17",   "JAE":      "18",   "JB":       "19",   "JBE":      "1a",
            "READ":     "1b",   "PRINT":    "1c"}

# Dict for the registers and the operands
register = {'A':    "0001", 'B':    "0002", "C":    "0003",
            "D":    "0004", "E":    "0005", "S":    "0006"}

# Dict for labels to prevent double multiply defined labels
label = {}
    

patterns = ["^\s*(\w+)\s+(\w+)\s*$", "^\s*(\w+)\s+('.*')\s*$", "^\s*(\w+)\s+(\".*\")\s*$", "^\s*(\w+)\s+(\[\w+\])\s*$","^\s*(\w+:)\s*()$","^\s*(\w+)\s*()$","^\s*()()$"]

isInstr = True
addressing_mode= ""
operand=""
counter=0

binFile = open("prog.bin", "w")
asm = None
with open(sys.argv[1], "r") as f:
    asm = f.read()
asm = asm.split("\n")


# For checking the location of the label and if it's defined before
for line in asm:       
    line = line.split()
    value = line[0] if len(line) != 0 else -1    # The whole line is assigned to the value variable. If the line is empty, value is -1
    opcode   = ""
    addrmode = ""
    operand  = ""

    if value == -1:                             # Skips the empty line
        continue

    elif value.__contains__(":"):               # Found the label
        value=value.replace(":", "")
        if value in label:                      # If defined before
            print("Label defined twice!")
        operand = hex((counter) * 3)[2:]
        label[value] = operand 
    else:                                       # Increments the counter in order to locate the label
        counter+=1

counter=0
for line in asm:
    syntax=False
    for i in range(len(patterns)):
        
        a = re.search(patterns[i],line)
        if a:
            if a.group(2):
                line = [a.group(1),a.group(2)]
            else:
                line = [a.group(1)]
            syntax = True
            counter+=1
            break
        else:
            continue
        
    if not syntax:
        print("Syntax Error at Line " + str(counter))
        break
        

    #line = line.split()
    value = line[0] if len(line) != 0 else -1
    opcode   = ""
    addrmode = ""
    operand  = ""
    if value == -1:
        continue
    elif value in instr:                        # Found an instruction
        opcode = instr[value]                   # Assigned its opcode
        isInstr = True                          
    else:
        isInstr = False                   
    
    if isInstr == True:                         # Skips the if block if the line doesn't contain any instruction
        if value == "HALT" or value == "NOP":
            addressing_mode = "0"
            operand = "00"

        # Finds the inputs formatted as "LOAD "x""" or "LOAD 'x'". It could contain any number of alphanumerical character
        elif (re.match("\'(.)\'", line[1]) != None) or (re.match("\"(.)\"", line[1]) != None):         # 'A'
            var=line[1][1:-1].encode('utf-8')
            operand = var.hex()
            addressing_mode = "0"
        
        # Finds the inputs formatted as "LOAD [x]"". It could contain only alphanumerical characters
        elif (re.match("\[(\w)\]", line[1]) != None):       # [A]
            var = line[1][1:-1]
            # If the character is one of the registers, addressing mode is 10, otherwise it's 11
            if register.__contains__(var):
                operand = register[var]
                addressing_mode = "2"
            else:                   
                addressing_mode = "3"

        # Finds the inputs from the registers, formatted as "LOAD A". Operand is pulled from the dict.
        elif (re.match("^[ABCDES]$", line[1]) != None):     # A
            var = line[1]
            operand = register[var]
            addressing_mode = "1"
        # Finds the inputs formatted as "LOAD [0b69f]". Brackets are deleted and the operand is the input on the left, 
        elif (re.match("^\[\d+\]$", line[1]) != None):     # A
            var = line[1]
            operand = var[1:-1]
            addressing_mode = "3"  
        # Finds the inputs containing labels, assings it's location from the dict to the operand.      
        elif label.__contains__(line[1]):
            var = label[line[1]]
            addressing_mode = "0"
            operand = var
        # Finds the inputs formatted as "LOAD 0b69f". Operand is the input on the left itself.
        else: 
            operand = line[1]
            addressing_mode = "0"
    
        
        # Taken from convert.py file
        opcode = int(str(opcode),16) 
        addressing_mode = int(str(addressing_mode),16)    
        operand  = int(str(operand),16) 

        bopcode = format(opcode, '06b')
        baddressing_mode = format(addressing_mode, '02b')
        boperand = format(operand, '016b') 

        bin = '0b' + bopcode + baddressing_mode + boperand 
        ibin = int(bin[2:],2) ; 
        result = format(ibin, '06x')
        binFile.write(result+"\n")