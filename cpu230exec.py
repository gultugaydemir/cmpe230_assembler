import sys
# Instructions are in big-endian, stack is in little-endian

# max 16 bit memory access (64k)
MAX_VAL = 2**16-1  # 0xFFFF
SIGN_BIT = 2**15
virt_mem = [0 for _ in range(MAX_VAL+1)]

# PC + alphabet letters = 27. PC->0, A->1, S->19, Z->26
regs = [0 for _ in range(27)]
regs[19] = MAX_VAL-1  # Stack must be #0xFFFE at start.

# Flags
SF = False
ZF = False
CF = False


class ProgError(Exception):  # For errors that should not have happened
    def __init__(self, msg):
        self.msg = msg


class Error(Exception):
    def __init__(self, msg, mem_inc):
        dump = hex(virt_mem[regs[0]]>>2)+" "+str(virt_mem[regs[0]]&3)+" "+str((virt_mem[regs[0]+1]<<8)+virt_mem[regs[0]+2])
        self.msg = "{} at memory: {}\nMemory Dump: {}".format(msg, regs[0]+mem_inc, dump)


class OpcodeError(Error):
    def __init__(self):
        super().__init__("Illegal opcode", -3)


class AddrModeError(Error):
    def __init__(self):
        super().__init__("Illegal addressing", -2)


class RegisterError(Error):
    def __init__(self):
        super().__init__("Non-existent register", -1)


class SetAddrError(Error):
    def __init__(self):
        super().__init__("Set command to data", -1)


class EndOfMemory(Error):
    def __init__(self):
        super().__init__("End of memory access", -1)


def not_op_16(val):
    return (~val) & MAX_VAL


def sub_op_16(v1, v2):
    return v1 + ((not_op_16(v2)+1) & MAX_VAL)


def read_operand(addr_mode, operand):
    if not 0 <= addr_mode < 4:
        raise ProgError("Non expected addr_mode: {}".format(addr_mode))
    if operand > MAX_VAL:
        raise ProgError("Overflow operand value: {}".format(operand))

    if addr_mode == 0:
        return operand
    if addr_mode == 3:
        if operand == MAX_VAL:
            raise EndOfMemory
        return (virt_mem[operand] << 8) + virt_mem[operand+1]

    if not 0 <= operand < 27:
        raise RegisterError

    if addr_mode == 1:
        return regs[operand]
    if addr_mode == 2:
        if regs[operand] == MAX_VAL:
            raise EndOfMemory
        return (virt_mem[regs[operand]] << 8) + virt_mem[regs[operand]+1]


def store_to_operand(addr_mode, operand, value):
    if not 0 <= addr_mode < 4:
        raise ProgError("Non expected addr_mode: {}".format(addr_mode))
    if operand > MAX_VAL:
        raise ProgError("Overflow operand value: {}".format(operand))

    if addr_mode == 0:
        raise SetAddrError

    if addr_mode == 3:
        if operand == MAX_VAL:
            raise EndOfMemory
        virt_mem[operand] = value >> 8
        virt_mem[operand+1] = value & 255

    if not 0 <= operand < 27:
        raise RegisterError

    if addr_mode == 1:
        regs[operand] = value
    if addr_mode == 2:
        if regs[operand] == MAX_VAL:
            raise EndOfMemory
        virt_mem[regs[operand]] = value >> 8
        virt_mem[regs[operand]+1] = value & 255


def set_flags(value):  # Set flags except carry
    global SF, ZF
    SF = False
    ZF = False
    if (value & SIGN_BIT) != 0:
        SF = True
    elif value == 0:
        ZF = True


def halt():
    exit(0)


def load(addr_mode, operand):
    regs[1] = read_operand(addr_mode, operand)


def store(addr_mode, operand):
    store_to_operand(addr_mode, operand, regs[1])


def add(addr_mode, operand):
    global CF
    regs[1] += read_operand(addr_mode, operand)
    CF = (regs[1] & (MAX_VAL+1))!=0
    regs[1] &= MAX_VAL
    set_flags(regs[1])


def sub(addr_mode, operand):
    global CF
    regs[1] = sub_op_16(regs[1], read_operand(addr_mode, operand))
    CF = (regs[1] & (MAX_VAL+1))!=0
    regs[1] &= MAX_VAL
    set_flags(regs[1])


def inc(addr_mode, operand):
    global CF
    value = read_operand(addr_mode, operand) + 1
    CF = (value & (MAX_VAL+1))!=0
    value &= MAX_VAL
    set_flags(value)
    store_to_operand(addr_mode, operand, value)


def dec(addr_mode, operand):
    global CF
    value = read_operand(addr_mode, operand) + MAX_VAL
    CF = (value & (MAX_VAL+1))!=0
    value &= MAX_VAL
    set_flags(value)
    store_to_operand(addr_mode, operand, value)


def _xor(addr_mode, operand):
    regs[1] ^= read_operand(addr_mode, operand)
    set_flags(regs[1])


def _and(addr_mode, operand):
    regs[1] &= read_operand(addr_mode, operand)
    set_flags(regs[1])


def _or(addr_mode, operand):
    regs[1] |= read_operand(addr_mode, operand)
    set_flags(regs[1])


def _not(addr_mode, operand):
    value = not_op_16(read_operand(addr_mode, operand))
    set_flags(value)
    store_to_operand(addr_mode, operand, value)


def shl(addr_mode, operand):
    global CF
    value = read_operand(addr_mode, operand) << 1
    CF = (value & (MAX_VAL+1))!=0
    value &= MAX_VAL
    set_flags(value)
    store_to_operand(addr_mode, operand, value)


def shr(addr_mode, operand):
    value = read_operand(addr_mode, operand) >> 1
    value &= MAX_VAL
    set_flags(value)
    store_to_operand(addr_mode, operand, value)


def nop():
    pass


def push(addr_mode, operand):
    if regs[19] <= 2:
        raise EndOfMemory
    value = read_operand(addr_mode, operand)
    virt_mem[regs[19]] = value >> 8
    virt_mem[regs[19]-1] = value & 255
    regs[19] -= 2


def pop(addr_mode, operand):
    if regs[19] >= MAX_VAL-1:
        raise EndOfMemory
    value = (virt_mem[regs[19]+2] << 8) + virt_mem[regs[19]+1]
    regs[19] += 2
    store_to_operand(addr_mode, operand, value)


def cmp(addr_mode, operand):
    global CF
    value = sub_op_16(regs[1], read_operand(addr_mode, operand))
    CF = (value & (MAX_VAL+1))!=0
    value &= MAX_VAL
    set_flags(value)

def jmp(addr_mode, operand):
    regs[0] = read_operand(addr_mode, operand)
    if regs[0] >= MAX_VAL-1:
        raise EndOfMemory

def jz(addr_mode, operand):
    global ZF
    if ZF:
        jmp(addr_mode, operand)

def jnz(addr_mode, operand):
    global ZF
    if not ZF:
        jmp(addr_mode, operand)

def jc(addr_mode, operand):
    global CF
    if CF:
        jmp(addr_mode, operand)

def jnc(addr_mode, operand):
    global CF
    if not CF:
        jmp(addr_mode, operand)

def ja(addr_mode, operand):
    global ZF, SF
    if (not ZF) and (not SF):
        jmp(addr_mode, operand)

def jae(addr_mode, operand):
    global ZF, SF
    if ZF or (not SF):
        jmp(addr_mode, operand)

def jb(addr_mode, operand):
    global ZF, SF
    if (not ZF) and SF:
        jmp(addr_mode, operand)

def jbe(addr_mode, operand):
    global ZF, SF
    if ZF or SF:
        jmp(addr_mode, operand)

def _read(addr_mode, operand):
    store_to_operand(addr_mode, operand, ord(input()[0]))

def _print(addr_mode, operand):
    print(chr(read_operand(addr_mode, operand)))

# Instructions are numbered from 1 to 29.
# In this array, they are indexed from 0 to 28.
executionArr = [
    lambda addr_mode, operand: halt(),
    lambda addr_mode, operand: load(addr_mode, operand),
    lambda addr_mode, operand: store(addr_mode, operand),
    lambda addr_mode, operand: add(addr_mode, operand),
    lambda addr_mode, operand: sub(addr_mode, operand),
    lambda addr_mode, operand: inc(addr_mode, operand),
    lambda addr_mode, operand: dec(addr_mode, operand),
    lambda addr_mode, operand: _xor(addr_mode, operand),
    lambda addr_mode, operand: _and(addr_mode, operand),
    lambda addr_mode, operand: _or(addr_mode, operand),
    lambda addr_mode, operand: _not(addr_mode, operand),
    lambda addr_mode, operand: shl(addr_mode, operand),
    lambda addr_mode, operand: shr(addr_mode, operand),
    lambda addr_mode, operand: nop(),
    lambda addr_mode, operand: push(addr_mode, operand),
    lambda addr_mode, operand: pop(addr_mode, operand),
    lambda addr_mode, operand: cmp(addr_mode, operand),
    lambda addr_mode, operand: jmp(addr_mode, operand),
    lambda addr_mode, operand: jz(addr_mode, operand),
    lambda addr_mode, operand: jnz(addr_mode, operand),
    lambda addr_mode, operand: jc(addr_mode, operand),
    lambda addr_mode, operand: jnc(addr_mode, operand),
    lambda addr_mode, operand: ja(addr_mode, operand),
    lambda addr_mode, operand: jae(addr_mode, operand),
    lambda addr_mode, operand: jb(addr_mode, operand),
    lambda addr_mode, operand: jbe(addr_mode, operand),
    lambda addr_mode, operand: _read(addr_mode, operand),
    lambda addr_mode, operand: _print(addr_mode, operand)
]


# Read file to virtual memory
with open(sys.argv[1], "r") as binfile:
    memwrite = 0
    for cmd in binfile:
        str_bytes = format(int(cmd, 16), "024b")
        for ind in range(3):
            virt_mem[memwrite] = int(str_bytes[ind*8:(ind+1)*8], 2)
            memwrite += 1

try:
    regs[0] = 0
    while True:
        opcode = virt_mem[regs[0]] >> 2
        addr_mode = virt_mem[regs[0]] & 3
        operand = (virt_mem[regs[0]+1] << 8)+virt_mem[regs[0]+2]

        if not 0 < opcode <= len(executionArr):  # < 30:
            raise OpcodeError()

        # Instructions have been read
        regs[0] += 3

        # Index on array + 1 = Instruction code
        executionArr[opcode-1](addr_mode, operand)

except Error as err:
    print(err.msg)
except ProgError as err:
    print(err.msg)
    print("This should not have happened :(")
