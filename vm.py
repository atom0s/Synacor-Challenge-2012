'''
Synacor Virtual Machine - Copyright (c) 2022 atom0s [atom0s@live.com]

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
import sys


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


class VirtualMachine():
    '''
    Implements the Synacor challenge virtual machine.

    Properties
    -------------------------

    ops - dictionary
        The dictionary of opcode information, implemented by the virtual machine.

    reg - list[int]
        The virtual machine registers.

    stk - list[int]
        The virtual machine stack.

    mem - list[int]
        The loaded binary file data to be processed by the virtual machine. Broken into uint16_t entries.

    pos - int
        The current execution position of the virutal machine within the 'mem'.

    hlt - bool
        The virtual machine halt flag; stops execution if set to True.

    out - string
        The output buffer to hold building strings to be printed to the user when a newline is reached.

    inc - string
        The incoming buffer to hold building strings to be used for custom input commands.

    hst - list
        The input command history that can be dumped for later reusage.
    '''

    ops = {}
    reg = [0, 0, 0, 0, 0, 0, 0, 0]
    stk = []
    mem = []
    pos = 0
    hlt = False
    out = ''
    inc = ''
    hst = []

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

        self.reg = [0, 0, 0, 0, 0, 0, 0, 0]
        self.stk = []
        self.mem = []
        self.pos = 0
        self.hlt = False
        self.out = ''
        self.inc = ''
        self.hst = []

        if not os.path.exists(path):
            return False

        s = os.path.getsize(path)

        with open(path, 'rb') as f:
            for _ in range(int(s / 2)):
                self.mem.append(struct.unpack('H', f.read(2))[0])

        return True

    def load_test(self):
        '''
        Loads the challenge test sample program into the virtual machine.

        @param {VM} self - The VM object instance.
        @return {bool} True on success, false otherwise.
        @notes

            This test program comes from the arch-spec documentation. However, it is modified, slightly, to work properly with
            my VM and to add proper termination instead of just running until error. The program is designed to:

                - Store into register 0, the sum of 4 and the value contained in register 1. ie. reg[0] = 4 + reg[1]
                - Output to the terminal, the character with the ascii code contained in register 0. ie. printf(char(reg[0]))

            Due to how my VM works with output, the output buffer is not printed until a newline is hit. Thus, I have appended
            the opcode information needed to produce a newline write. I also append the halt opcode to allow the program to properly
            terminate instead of running past the data buffer and erroring out to exit.

            Register 1 is set to the ascii code value for 'A', thus, with the given notes, the program should output 'E'.
        '''

        self.reg = [0, 0, 0, 0, 0, 0, 0, 0]
        self.stk = []
        self.mem = []
        self.pos = 0
        self.hlt = False
        self.out = ''
        self.inc = ''
        self.hst = []

        self.mem = [0x0009, 0x8000, 0x8001, 0x0004, 0x0013, 0x8000]
        self.mem.append(0x0013)
        self.mem.append(0x000A)
        self.mem.append(0x0000)
        self.reg[1] = ord('A')

        return True

    def run(self):
        '''
        Executes the virtual machine, processing the loaded data.

        @param {VM} self - The VM object instance.
        '''

        while not self.hlt and self.pos < len(self.mem):
            opcode = self.mem[self.pos]

            try:
                _, args, func = self.ops[opcode]

                if not func():
                    self.pos += args + 1

            except BaseException as f:
                print('[!] Caught exception while executing virtual machine:')
                raise f

    def val(self, n):
        '''
        Returns the translated value.

        @param {VM} self - The VM object instance.
        @param {int} n - The number to use for translation.
        @return {int} The translated number.

        @notes:
            - numbers 0..32767 mean a literal value
            - numbers 32768..32775 instead mean registers 0..7
            - numbers 32776..65535 are invalid
        '''

        if n <= 32767:
            return n
        elif n >= 32768 and n <= 32775:
            return self.reg[n - 32768]
        else:
            self.hlt = True

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
        self.hlt = True

        return False

    @opcode(0x01, 2, 'set')
    def op_set(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        self.reg[a - 32768] = self.val(b)

        return False

    @opcode(0x02, 1, 'push')
    def op_push(self):
        a = self.mem[self.pos + 1]

        self.stk.append(self.val(a))

        return False

    @opcode(0x03, 1, 'pop')
    def op_pop(self):
        if len(self.stk) == 0:
            self.hlt = True
            return False

        a = self.mem[self.pos + 1]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        self.reg[a - 32768] = self.stk.pop()

        return False

    @opcode(0x04, 3, 'eq')
    def op_eq(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]
        c = self.mem[self.pos + 3]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        self.reg[a - 32768] = 1 if self.val(b) == self.val(c) else 0

        return False

    @opcode(0x05, 3, 'gt')
    def op_gt(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]
        c = self.mem[self.pos + 3]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        self.reg[a - 32768] = 1 if self.val(b) > self.val(c) else 0

        return False

    @opcode(0x06, 1, 'jmp')
    def op_jmp(self):
        a = self.mem[self.pos + 1]

        self.pos = self.val(a)

        return True

    @opcode(0x07, 2, 'jt')
    def op_jt(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]

        if self.val(a) != 0:
            self.pos = self.val(b)
        else:
            self.pos += 3

        return True

    @opcode(0x08, 2, 'jf')
    def op_jf(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]

        if self.val(a) == 0:
            self.pos = self.val(b)
        else:
            self.pos += 3

        return True

    @opcode(0x09, 3, 'add')
    def op_add(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]
        c = self.mem[self.pos + 3]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        self.reg[a - 32768] = (self.val(b) + self.val(c)) % 32768

        return False

    @opcode(0x0A, 3, 'mult')
    def op_mult(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]
        c = self.mem[self.pos + 3]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        self.reg[a - 32768] = (self.val(b) * self.val(c)) % 32768

        return False

    @opcode(0x0B, 3, 'mod')
    def op_mod(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]
        c = self.mem[self.pos + 3]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        self.reg[a - 32768] = self.val(b) % self.val(c)

        return False

    @opcode(0x0C, 3, 'and')
    def op_and(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]
        c = self.mem[self.pos + 3]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        self.reg[a - 32768] = (self.val(b) & self.val(c)) % 32768

        return False

    @opcode(0x0D, 3, 'or')
    def op_or(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]
        c = self.mem[self.pos + 3]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        self.reg[a - 32768] = (self.val(b) | self.val(c)) % 32768

        return False

    @opcode(0x0E, 2, 'not')
    def op_not(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        self.reg[a - 32768] = (~self.val(b)) % 32768

        return False

    @opcode(0x0F, 2, 'rmem')
    def op_rmem(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        self.reg[a - 32768] = self.mem[self.val(b)]

        return False

    @opcode(0x10, 2, 'wmem')
    def op_wmem(self):
        a = self.mem[self.pos + 1]
        b = self.mem[self.pos + 2]

        self.mem[self.val(a)] = self.val(b)

        return False

    @opcode(0x11, 1, 'call')
    def op_call(self):
        a = self.mem[self.pos + 1]

        self.stk.append(self.pos + 2)
        self.pos = self.val(a)

        return True

    @opcode(0x12, 0, 'ret')
    def op_ret(self):
        if len(self.stk) == 0:
            self.hlt = True
            return False

        self.pos = self.stk.pop()

        return True

    @opcode(0x13, 1, 'out')
    def op_out(self):
        a = self.mem[self.pos + 1]

        if self.val(a) == 10:
            print(self.out)
            self.out = ''
        else:
            self.out += chr(self.val(a))

        return False

    @opcode(0x14, 1, 'in')
    def op_in(self):
        a = self.mem[self.pos + 1]

        if not self.is_reg(a):
            raise Exception('Invalid register index.')

        # Store the incoming data normally..
        self.reg[a - 32768] = ord(sys.stdin.read(1))

        # Store the incoming data locally..
        if self.reg[a - 32768] != 10:
            self.inc += chr(self.reg[a - 32768])
            return False

        # Store the command in the input history..
        self.hst.append(self.inc)

        # Cleanup the input buffer..
        s = self.inc
        self.inc = ''

        # Split the command into args..
        p = s.split(' ')

        if len(p) == 0:
            return False

        #
        # General Commands
        #

        # !help - Prints the available custom commands.
        if p[0] == '!help':
            print('[!] Available custom commands:\n')
            print('[!] Command: !help - Prints the available custom commands.')
            print('[!] Command: !history - Saves the past command history to \'commands.txt\' on disk.')
            print('[!] Command: !halt - Sets the halt flag, killing the VM.')
            print('[!] Command: !kill - Sets the halt flag, killing the VM.')
            print('[!] Command: !dump - Dumps the current VM memory to \'dump.bin\' on disk.')
            print('[!] Command: !pos - Prints the current execution position of the VM.')
            print('[!] Command: !getreg - Prints the current register values.')
            print('[!] Command: !getstack - Prints the current stack values.')
            print('[!] Command: !setreg <index> <value..> - Sets a register value.')
            print('[!] Command: !poke <index> <value..> - Writes value(s) to memory.')
            print('[!] Command: !peek <index> <count=1> - Reads value(s) from memory.')
            return False

        # !history - Saves the past command history to 'commands.txt' on disk.
        if p[0] == '!history':
            with open('history.txt', 'w') as f:
                for line in self.hst:
                    f.write(f'{line}\n')

            print(f'[!] Command history saved to: \'history.txt\'')
            return False

        #
        # Debugging Commands
        #

        # !halt - Sets the halt flag, killing the VM.
        # !kill - Sets the halt flag, killing the VM.
        if p[0] == '!halt' or p[0] == '!kill':
            self.hlt = True
            print('[!] Virtual machine has been halted by force.')
            return False

        # !dump - Dumps the current VM memory to 'dump.bin' on disk.
        if p[0] == '!dump':
            with open('dump.bin', 'wb') as f:
                for x in range(len(self.mem)):
                    f.write(struct.pack('H', self.mem[x]))

            print(f'[!] Memory dump saved to: \'dump.bin\'')
            return False

        # !pos - Prints the current execution position of the VM.
        if p[0] == '!pos':
            print(f'[!] Current execution position: {self.pos:04X} ({self.pos})')
            return False

        # !getreg - Prints the current register values.
        if p[0] == '!getreg':
            for n in range(8):
                print(f'[!] Register {n}: {self.reg[n]:04X} ({self.reg[n]})')

            return False

        # !getstack - Prints the current stack values.
        if p[0] == '!getstack':
            for n in range(len(self.stk)):
                print(f'[!] Stack {n}: {self.stk[n]:04X} ({self.stk[n]})')

            return False

        # !setreg <index> <value> - Sets a register value.
        if p[0] == '!setreg':
            p = list(map(lambda n: int(n, 16), s[8:].split(' ')))

            if len(p) != 2 or p[0] > 7 or p[1] > 32767:
                print('[!] Invalid arguments; !setreg <index> <value>')
                return False

            self.reg[p[0]] = p[1]

            print(f'[!] Register {p[0]} set to: {p[1]:04X}')
            return False

        # !poke <index> <value..> - Writes value(s) to memory.
        if p[0] == '!poke':
            p = list(map(lambda n: int(n, 16), s[6:].split(' ')))

            if len(p) < 2:
                print('[!] Invalid arguments; !poke <index> <value..>')
                return False

            if p[0] > len(self.mem):
                print('[!] Invalid memory index, cannot poke.')
                return False

            for x in range(1, len(p)):
                self.mem[p[0] + (x - 1)] = p[x]

            o = p.pop(0)

            print(f'[!] Memory written to {o:04X}: ' + ' '.join('{:04X}'.format(n) for n in p))
            return False

        # !peek <index> <count=1> - Reads value(s) from memory.
        if p[0] == '!peek':
            p = list(map(lambda n: int(n, 16), s[6:].split(' ')))

            if len(p) < 1:
                print('[!] Invalid arguments; !peek <index> <count=1>')
                return False

            if p[0] > len(self.mem):
                print('[!] Invalid memory index, cannot peek.')
                return False

            c = 1
            if len(p) >= 2:
                c = p[1]

            o = []
            for x in range(c):
                o.append(self.mem[p[0] + x])

            print(f'[!] Memory read from {p[0]:04X}: ' + ' '.join('{:04X}'.format(n) for n in o))
            return False

        return False

    @opcode(0x15, 0, 'noop')
    def op_noop(self):
        return False


def main(path, test):
    '''
    Main entry point, runs the virtual machine.

    @param {string} path - The binary data file path to be processed and executed.
    @param {bool} test - Flag if the virtual machine should run in test mode or not.
    '''

    # Run the test program..
    if test is True:
        vm = VirtualMachine()
        if vm.load_test():
            vm.run()

        return

    # Run the given binary file..
    if not os.path.exists(path):
        return

    # Load and run the VM..
    vm = VirtualMachine()
    if vm.load(path):
        vm.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser('Synacor challenge binary data file virtual machine.')
    parser.add_argument('--path', dest='path', default='data/challenge.bin', type=str, help='The path to the input file to run in the virtual machine.')
    parser.add_argument('--test', dest='test', default=False, type=bool, help='Tests the virtual machine by executing the challenge test program.')
    args = parser.parse_args()

    main(args.path, args.test)
