# A 4 bit computer simulation using Python to move 0's and 1's around

It uses 4 bit opcodes and 4 bit RAM addresses. It parsers 8 bit of data at once, and does not use more than 1 line for the same operation. 
It has 4 registers: 2 for general-purpose, 1 for program counter, and the other for instruction addresses.

So the maximum amount of instructions is 16 and the maximun amount of RAM is 16 bytes.

## Description

Currently it has these instructions:

* LDA (Load A) - Load contents of a given RAM reference to the register A;
* LDB (Load B) - Same as before, but for register B;
* STA (Store A) - Store contents of register A to a given RAM address;
* STB (Store B) - Same as before, but for register B;

* HTL (Halt) - Stops the computer execution;

* ADD (Addition) - Needs two parameters containing both registers. Add the first register to the second;
* SUB (Subtraction) - Same as ADD but for subtraction;

* JIE (Jump if equal) - Jumps to a given RAM address if register A's value is equal to register B's value;
* JNE (Jump if not equal) - Same as above, but only if values are not equal

The ALU has more operations that I haven't implemented on the CPU yet, like the bitwise ones. I'll be doing it in the future.


## The Assembly language

The assembler and its assembly syntax I made myself. I'm not experienced with assembly, so after an extensive read I came up with the most basic yet effective syntax I could think of for my simple 4 bit computer.

There's an already written [simple script](scripts/count_to_ten.asm) on `/scripts` if you want to quick see how the syntax is like.

### Comments

Any line without instructions contaning a `;` sign will be ignored. If the line contains code, anything after the `;` sign will be ignored:

```asm
section. data
    someVariable = 0    ; hey look! it's an empty variable!
```

### `section .data`

Here is where you declare your variables. The syntax is like this:

```asm
section .data
    variableName = 2
```

#### Variable Name: 

`section` is a reserved keyword. You may utilize anything else. No spaces.


#### Value: 

Yoy may pass a direct integer value (between 0-255) or you may pass a RAM address reference using the `$` sign. It needs to be an integer and it will select 
an horizontal line of the RAM (1 byte):

```asm
section. data
    variableWithDirectValue = 255
    someValueInRam = $15
```

On that example, since the computer RAM is 16 bytes, it would select the last byte.

### `section .text`

Here is where you declare the instructions for the computer to execute. You may get a reference to the registers like this:

* `ax`: references register A;
* `bx`: references register B;

Here are all the instructions and its syntax:

#### `ld [register], [ramAddress | variableName]`

Loads the content of the given RAM addres or the variable into the selected register:

```asm
ld ax, someVariable
```

#### `st [register], [ramAddress | variableName]`

Stores the content inside the register to the given RAM address or the variable:

```asm
st bx, $10
```

#### `add [ax | bx], [ax | bx]`

Add two registers together, and the output is saved on the last register reference sent. On this example:

```asm
add ax, bx
```
`ax` would be added to `bx` and the result would be stored inside `bx`.

#### `sub [ax | bx], [ax | bx]`

Same as before, doesn't need further explanation. Just be aware of negative numbers.

#### `jie [variableName | ramReference]`

Jumps to the given RAM reference/variable name if `ax`'s value is equal to `bx`s: 

```asm
section. text
    jie $0      ; infinite loop
```

#### `jne [variableName | ramReference]`

Same as above, but jump only if `ax`'s value is not equal to `bx`'s value.


## Getting Started

### Dependencies

Just clone this repo and setup the Python interpreter and you're done.

### Executing program

After cloning the repo, you don't really need to setup anything else besides the Python interpreter. 
You can use the `asm-cli.py` CLI to do the compilation and run the program:

```
python3 asm-cli.py path_to_asm_script.asm
```

This would compile that script and output it to the same folder, with the same name, but with the extension `.bin`.

To set an output_folder, send another argument after the `asm_file_path` argument:

```
python3 asm-cli.py path_to_asm_script.asm output_folder
```

To run it, you can do:

```
python3 asm-cli.py path_to_bin_file.bin
```

You can also compile and run with a single command:

```
python3 asm-cli.py -run path_to_asm_script.asm
```


## License

This project is licensed under the MIT License - see the LICENSE.md file for details
