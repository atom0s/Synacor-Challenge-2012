# Synacor OSCON Challenge Solution (2012)

This repository contains my code and solution to solve the Synacor OSCON 2012 Challenge. 

If you are interested in checking out or trying the challenge for yourself, it can be found online still here:

https://challenge.synacor.com/

## Notes

Firstly, please understand this is an old challenge. I am not the first to solve it, not even close, and this was solely done because a friend suggested it to me on Discord this past week. I never saw the challenge before and since it involved implementation of a VM, it was something I was interested in checking out since it has been a topic I've been involved in recently.

Next, the challenge is still online and fully functional. Because of that, it is important to note that if you do sign up and decide to try the challenge, the information in this solution will work but the flags (codes) you need will be different. The challenge generates unique flags for each player. _(The `challenge.bin` data file is unique to each player.)_ If you try to use my flags, you will get an error.

Lastly, I used this challenge as a means to continue with my progress of learning Python. So please excuse the messy code and probably poor / old means of which I did some things. I'm sure there are much better ways to code various things I made, but I am still fairly new to Python. 

## Repository Information

**You can read my full solution here:** [Full Solution](SOLUTION.md)

In order to solve the challenge, the main task you are given is to implement a virtual machine that can emulate the given opcodes found within the challenge `arch-spec` file. To handle this part of the challenge, and assisting with other parts, I wrote the virtual machine and a disassembler for the binary data file in Python.

  * **Virtual Machine:** [Virtual Machine Implementation](vm.py)
  * **Disassembler:** [Disassembler Implementation](dism.py)

Throughout the challenge, once the VM is functional, there are puzzles to be solved. The three puzzles all required their own implementation of code to be solved. Two of the puzzles I was able to solve in Python, however the other was too slow to implement in Python alone. Instead, I opt'd to use C++ for that one instead. _(I made a Python implementation using ghetto threading, but it's ugly and slow so not worth including.)_

The first puzzle is within the `Ruins` area of the game. My solver for that can be found here:

  * **Ruins Puzzle (Coins):** [Ruins Puzzle Solver](ruins.py)

The next puzzle, which required the C++ implementation to not be ungodly slow, is for the `teleporter` item puzzle. That can be found here:

  * **Teleporter Puzzle:** [Teleport Puzzle Solver](ackermann/synacor_ackermann/main.cpp)

The final puzzle, in the `Vault` area, can be solved with my solution here:

  * **Vault Puzzle:** [Vault Puzzle Solver](vault.py)

Other files included in the repo are:

  - [arch-spec](data/arch-spec) - The challenge documentation.
  - [challenge.bin](data/challenge.bin) - My unique `challenge.bin` binary data file.
  - [Disassembler Dump](data/dism.txt) - A full dump of my `challenge.bin` disassembly.
  
## Challenge Information

```
== Synacor Challenge ==
In this challenge, your job is to use this architecture spec to create a
virtual machine capable of running the included binary.  Along the way,
you will find codes; submit these to the challenge website to track
your progress.  Good luck!


== architecture ==
- three storage regions
  - memory with 15-bit address space storing 16-bit values
  - eight registers
  - an unbounded stack which holds individual 16-bit values
- all numbers are unsigned integers 0..32767 (15-bit)
- all math is modulo 32768; 32758 + 15 => 5

== binary format ==
- each number is stored as a 16-bit little-endian pair (low byte, high byte)
- numbers 0..32767 mean a literal value
- numbers 32768..32775 instead mean registers 0..7
- numbers 32776..65535 are invalid
- programs are loaded into memory starting at address 0
- address 0 is the first 16-bit value, address 1 is the second 16-bit value, etc

== execution ==
- After an operation is executed, the next instruction to read is immediately after the last argument of the current operation.  If a jump was performed, the next operation is instead the exact destination of the jump.
- Encountering a register as an operation argument should be taken as reading from the register or setting into the register as appropriate.

== hints ==
- Start with operations 0, 19, and 21.
- Here's a code for the challenge website: fNCoeXxLEawt
- The program "9,32768,32769,4,19,32768" occupies six memory addresses and should:
  - Store into register 0 the sum of 4 and the value contained in register 1.
  - Output to the terminal the character with the ascii code contained in register 0.

== opcode listing ==
halt: 0
  stop execution and terminate the program
set: 1 a b
  set register <a> to the value of <b>
push: 2 a
  push <a> onto the stack
pop: 3 a
  remove the top element from the stack and write it into <a>; empty stack = error
eq: 4 a b c
  set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise
gt: 5 a b c
  set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise
jmp: 6 a
  jump to <a>
jt: 7 a b
  if <a> is nonzero, jump to <b>
jf: 8 a b
  if <a> is zero, jump to <b>
add: 9 a b c
  assign into <a> the sum of <b> and <c> (modulo 32768)
mult: 10 a b c
  store into <a> the product of <b> and <c> (modulo 32768)
mod: 11 a b c
  store into <a> the remainder of <b> divided by <c>
and: 12 a b c
  stores into <a> the bitwise and of <b> and <c>
or: 13 a b c
  stores into <a> the bitwise or of <b> and <c>
not: 14 a b
  stores 15-bit bitwise inverse of <b> in <a>
rmem: 15 a b
  read memory at address <b> and write it to <a>
wmem: 16 a b
  write the value from <b> into memory at address <a>
call: 17 a
  write the address of the next instruction to the stack and jump to <a>
ret: 18
  remove the top element from the stack and jump to it; empty stack = halt
out: 19 a
  write the character represented by ascii code <a> to the terminal
in: 20 a
  read a character from the terminal and write its ascii code to <a>; it can be assumed that once input starts, it will continue until a newline is encountered; this means that you can safely read whole lines from the keyboard and trust that they will be fully read
noop: 21
  no operation
```
