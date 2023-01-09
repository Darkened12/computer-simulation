# ------------------------------------------------------------------------------------------------------------------ #
# ************** This is an CLI for the compiler/assembler. It can also run .asm on the fly on the computer. ******* #
# ------------------------------------------------------------------------------------------------------------------ #


import os
import sys
from typing import List

from compiler.assembler import Assembler


def _assembler_stderr(warning: str, message: str) -> None:
    print(f'[Assembler] ({warning}): {message}', file=sys.stderr)


def _bin_loader(path_to_bin_file: str) -> List[str]:
    with open(path_to_bin_file, 'r') as file:
        return list(map(lambda line: line.replace('\n', ''), file.readlines()))


def _main():
    if len(sys.argv) <= 1:
        return _assembler_stderr('Error', 'This is a command line interface. Please run it with the necessary arguments'
                                          '. example: "python3 asm-cli.py my_script.asm"')

    should_also_run = False

    if '-run' in sys.argv:
        sys.argv.pop(sys.argv.index('-run'))
        should_also_run = True

    try:
        assembly_file_path = sys.argv[1]
    except IndexError:
        return _assembler_stderr('Error', 'Missing "file_path" parameter')

    if not os.path.isfile(assembly_file_path):
        assembly_file_path = f'{os.getcwd()}\\{assembly_file_path}'
        if not os.path.isfile(assembly_file_path):
            return _assembler_stderr('Error', f'file "{assembly_file_path}" does not exist')

    run_only = assembly_file_path.endswith('.bin')

    if not run_only:
        if not assembly_file_path.endswith('.asm'):
            return _assembler_stderr('Error', 'Wrong file format. It should end with ".asm"')

        try:
            output_folder = sys.argv[2]
        except IndexError:
            output_folder = None
            _assembler_stderr('Warning', 'output_folder not set. Using the current assembly script folder as '
                                         'the output folder')

        asm = Assembler(path_to_assembly_file=assembly_file_path, output_path=output_folder)
        output_file_path = asm.compile()

    else:
        if not assembly_file_path.endswith('.bin'):
            return _assembler_stderr('Error', 'Wrong file format. It should end with ".bin"')

        output_file_path = assembly_file_path

    if should_also_run or run_only:
        from computer.cpu import CentralProcessingUnit
        cpu = CentralProcessingUnit()
        cpu.ram.from_list(_bin_loader(output_file_path))
        cpu.run()
        cpu.status()


if __name__ == '__main__':
    _main()
