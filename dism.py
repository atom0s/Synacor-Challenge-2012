'''
Synacor Disassembler - Copyright (c) 2022 atom0s [atom0s@live.com]

This work is licensed under the Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-nd/4.0/ or send a letter to
Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

By using this software, you agree to the above license and its terms.

    Attribution - You must give appropriate credit, provide a link to the license and indicate if changes were
                made. You must do so in any reasonable manner, but not in any way that suggests the licensor
                endorses you or your use.

Non-Commercial - You may not use the material for commercial purposes.

No-Derivatives - If you remix, transform, or build upon the material, you may not distribute the
                modified material. You are, however, allowed to submit the modified works back to the original
                project in attempt to have it added to the original project.

You may not apply legal terms or technological measures that legally restrict others
from doing anything the license permits.

No warranties are given.
'''

import argparse
import os
import struct


def opcode(o, a, n):
    '''
    Decorator for opcode handlers to set some basic information.

    @param {int} o - The opcode id.
    @param {int} a - The number of arguments the opcode uses.
    @param {string} n - The name of the opcode.
    '''
    def decorator(self):
        '''
        Adds the outer passed parameters to the function as attributes.
        '''

        self.opcode = o
        self.args = a
        self.name = n

        return self

    return decorator


class Disassembler():
    '''
    Implements a disassembler for the Synacor challenge virtual machine.

    Properties
    -------------------------

    ops - dictionary
        The dictionary of opcode information.

    pos - int
        The current position within the 'mem' being processed.

    mem - list
        The loaded binary file data, broken into uint16_t entries.
    '''

    ops = {}
    pos = 0
    mem = []

    def __init__(self):
        '''
        Initializes the virtual machine information.

        @param {VM} self - The VM object instance.
        '''

        for f in [getattr(self, k) for k in dir(self)]:
            if hasattr(f, '__func__') and hasattr(f.__func__, 'opcode'):
                self.ops[getattr(f.__func__, 'opcode')] = (getattr(f.__func__, 'name'), getattr(f.__func__, 'args'), f)

    def load(self, path):
        '''
        Loads the given file as the binary data to be executed in the VM.

        @param {VM} self - The VM object instance.
        @param {string} path - The path to the binary data to be loaded.
        @return {bool} True on success, false otherwise.
        '''

        # Reset the disassembler properties..
        self.pos = 0
        self.mem = []

        if not os.path.exists(path):
            return False

        s = os.path.getsize(path)

        with open(path, 'rb') as f:
            for _ in range(int(s / 2)):
                self.mem.append(struct.unpack('H', f.read(2))[0])

        return True

    def run(self):
        '''
        Steps the instructions of the loaded file, disassembling the data.

        @param {VM} self - The VM object instance.
        '''

        while self.pos < len(self.mem):
            opcode = self.mem[self.pos]

            try:
                name, args, func = self.ops[opcode]
                s = ''

                if args == 0:
                    s += int.to_bytes(opcode, 2, 'little').hex(' ').upper() + ' '
                elif args == 1:
                    s += int.to_bytes(opcode, 2, 'little').hex(' ').upper() + ' '
                    s += int.to_bytes(self.mem[self.pos + 1], 2, 'little').hex(' ').upper() + ' '
                elif args == 2:
                    s += int.to_bytes(opcode, 2, 'little').hex(' ').upper() + ' '
                    s += int.to_bytes(self.mem[self.pos + 1], 2, 'little').hex(' ').upper() + ' '
                    s += int.to_bytes(self.mem[self.pos + 2], 2, 'little').hex(' ').upper() + ' '
                elif args == 3:
                    s += int.to_bytes(opcode, 2, 'little').hex(' ').upper() + ' '
                    s += int.to_bytes(self.mem[self.pos + 1], 2, 'little').hex(' ').upper() + ' '
                    s += int.to_bytes(self.mem[self.pos + 2], 2, 'little').hex(' ').upper() + ' '
                    s += int.to_bytes(self.mem[self.pos + 3], 2, 'little').hex(' ').upper() + ' '
                else:
                    raise Exception('Invalid argument count.')

                print(f'{self.pos:04X} | {s:24s} | {name:5s} | {func()}')
                self.pos += args + 1

                # Manual linebreaks after jumps and rets to break apart 'function' blocks..
                if opcode == 0x00 or opcode == 0x06 or opcode == 0x12:
                    print('')

            except BaseException as e:
                s = int.to_bytes(self.mem[self.pos], 2, 'little').hex(' ').upper() + ' '
                print(f'{self.pos:04X} | {s:24s} | mem   | {self.mem[self.pos]:04X} (d: {self.mem[self.pos]})')
                self.pos += 1

    def val(self, n):
        '''
        Returns a virtual machine designed value based on various conditions.

        @param {VM} self - The VM object instance.
        @param {int} n - The number to use for translation.
        @return {int} The translated number.

        @notes:
            - numbers 0..32767 mean a literal value
            - numbers 32768..32775 instead mean registers 0..7
            - numbers 32776..65535 are invalid
        '''

        if n < 32768:
            return n
        elif n >= 32768 and n <= 32775:
            return n - 32768
        else:
            raise Exception('Invalid value.')

    def is_reg(self, n):
        '''
        Returns if the given value is a register index or not.

        @param {VM} self - The VM object instance.
        @param {int} n - The number to check.
        @return {bool} True if register index, false otherwise.
        '''
        return n >= 32768 and n <= 32775

    @opcode(0x00, 0, 'halt')
    def op_halt(self):
        return 'hault'

    @opcode(0x01, 2, 'set')
    def op_set(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        s = f'reg[{self.val(a)}] = '
        if (self.is_reg(b)):
            s += f'reg[{self.val(b)}]'
        else:
            s += f'{self.val(b):04X}'

        return s

    @opcode(0x02, 1, 'push')
    def op_push(self):
        a = self.mem[self.pos + 1]

        if self.is_reg(a):
            s = f'push reg[{self.val(a)}]'
        else:
            s = f'push {self.val(a):04X}'

        return s

    @opcode(0x03, 1, 'pop')
    def op_pop(self):
        a = self.mem[self.pos + 1]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        return f'reg[{self.val(a)}] = stack.pop()'

    @opcode(0x04, 3, 'eq')
    def op_eq(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]
        c = self.mem[self.pos + 3]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        s_b = f'reg[{self.val(b)}]' if self.is_reg(b) else f'{self.val(b):04X}'
        s_c = f'reg[{self.val(c)}]' if self.is_reg(c) else f'{self.val(c):04X}'

        return f'reg[{self.val(a)}] = {s_b} == {s_c}'

    @opcode(0x05, 3, 'gt')
    def op_gt(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]
        c = self.mem[self.pos + 3]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        s_b = f'reg[{self.val(b)}]' if self.is_reg(b) else f'{self.val(b):04X}'
        s_c = f'reg[{self.val(c)}]' if self.is_reg(c) else f'{self.val(c):04X}'

        return f'reg[{self.val(a)}] = {s_b} > {s_c}'

    @opcode(0x06, 1, 'jmp')
    def op_jmp(self):
        a = self.mem[self.pos + 1]

        return f'jmp reg[{self.val(a)}]' if self.is_reg(a) else f'jmp {self.val(a):04X}'

    @opcode(0x07, 2, 'jt')
    def op_jt(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]

        s_a = f'reg[{self.val(a)}]' if self.is_reg(a) else f'{self.val(a):04X}'
        s_b = f'reg[{self.val(b)}]' if self.is_reg(b) else f'{self.val(b):04X}'

        return f'jnz {s_b} : ({s_a} != 0)'

    @opcode(0x08, 2, 'jf')
    def op_jf(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]

        s_a = f'reg[{self.val(a)}]' if self.is_reg(a) else f'{self.val(a):04X}'
        s_b = f'reg[{self.val(b)}]' if self.is_reg(b) else f'{self.val(b):04X}'

        return f'jz {s_b} : ({s_a} == 0)'

    @opcode(0x09, 3, 'add')
    def op_add(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]
        c = self.mem[self.pos + 3]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        s_b = f'reg[{self.val(b)}]' if self.is_reg(b) else f'{self.val(b):04X}'
        s_c = f'reg[{self.val(c)}]' if self.is_reg(c) else f'{self.val(c):04X}'

        return f'reg[{self.val(a)}] = ({s_b} + {s_c}) % 32768'

    @opcode(0x0A, 3, 'mult')
    def op_mult(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]
        c = self.mem[self.pos + 3]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        s_b = f'reg[{self.val(b)}]' if self.is_reg(b) else f'{self.val(b):04X}'
        s_c = f'reg[{self.val(c)}]' if self.is_reg(c) else f'{self.val(c):04X}'

        return f'reg[{self.val(a)}] = ({s_b} * {s_c}) % 32768'

    @opcode(0x0B, 3, 'mod')
    def op_mod(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]
        c = self.mem[self.pos + 3]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        s_b = f'reg[{self.val(b)}]' if self.is_reg(b) else f'{self.val(b):04X}'
        s_c = f'reg[{self.val(c)}]' if self.is_reg(c) else f'{self.val(c):04X}'

        return f'reg[{self.val(a)}] = {s_b} % {s_c}'

    @opcode(0x0C, 3, 'and')
    def op_and(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]
        c = self.mem[self.pos + 3]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        s_b = f'reg[{self.val(b)}]' if self.is_reg(b) else f'{self.val(b):04X}'
        s_c = f'reg[{self.val(c)}]' if self.is_reg(c) else f'{self.val(c):04X}'

        return f'reg[{self.val(a)}] = ({s_b} & {s_c}) % 32768'

    @opcode(0x0D, 3, 'or')
    def op_or(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]
        c = self.mem[self.pos + 3]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        s_b = f'reg[{self.val(b)}]' if self.is_reg(b) else f'{self.val(b):04X}'
        s_c = f'reg[{self.val(c)}]' if self.is_reg(c) else f'{self.val(c):04X}'

        return f'reg[{self.val(a)}] = ({s_b} | {s_c}) % 32768'

    @opcode(0x0E, 2, 'not')
    def op_not(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        s_b = f'reg[{self.val(b)}]' if self.is_reg(b) else f'{self.val(b):04X}'

        return f'reg[{self.val(a)}] = (~{s_b}) % 32768'

    @opcode(0x0F, 2, 'rmem')
    def op_rmem(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        s_b = f'reg[{self.val(b)}]' if self.is_reg(b) else f'{self.val(b):04X}'

        if self.is_reg(b):
            return f'reg[{self.val(a)}] = mem[{s_b}]'

        return f'reg[{self.val(a)}] = mem[{s_b}] : ({self.mem[self.val(b)]:04X})'

    @opcode(0x10, 2, 'wmem')
    def op_wmem(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]

        s_a = f'reg[{self.val(a)}]' if self.is_reg(a) else f'{self.val(a):04X}'
        s_b = f'reg[{self.val(b)}]' if self.is_reg(b) else f'{self.val(b):04X}'

        return f'mem[{s_a}] = {s_b}'

    @opcode(0x11, 1, 'call')
    def op_call(self):
        a = self.mem[self.pos + 1]

        s_a = f'reg[{self.val(a)}]' if self.is_reg(a) else f'{self.val(a):04X}'

        return f'call {s_a}'

    @opcode(0x12, 0, 'ret')
    def op_ret(self):
        return 'ret'

    @opcode(0x13, 1, 'out')
    def op_out(self):
        a = self.val(self.mem[self.pos + 1])

        if a == 0:
            return '\\x00'
        elif a == 10:
            return '\\n'

        if a >= 0x100:
            return '<unk char>'

        return chr(a)

    @opcode(0x14, 1, 'in')
    def op_in(self):
        a = self.mem[self.pos + 1]

        return f'reg[{self.val(a)}] = (user input)'

    @opcode(0x15, 0, 'noop')
    def op_noop(self):
        return 'noop'


def main(path):
    '''
    Runs the disassembler.

    @param {string} path - The path to the file to disassemble.
    '''

    if not os.path.exists(path):
        return

    dism = Disassembler()
    dism.load(path)
    dism.run()


if __name__ == "__main__":
    '''
    Entry point.
    '''

    parser = argparse.ArgumentParser('Synacor challenge binary data file disassembler.')
    parser.add_argument('--path', dest='path', default='data/challenge.bin', type=str, help='The path to the input file to disassemble.')

    args = parser.parse_args()

    main(args.path)
