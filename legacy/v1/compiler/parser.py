from typing import List, Dict, Optional

from .errors import CompilerError


def _load_assembly_file(path_to_file: str) -> List[str]:
    """Returns a list where each item is a line of the code."""
    with open(path_to_file, 'r') as file:
        return file.readlines()


def _parse_newline(assembly_code: List[str]) -> List[str]:
    """Returns a new list without any \n."""
    return list(map(
        lambda line: line.replace('\n', ''), assembly_code)
    )


def _parse_whitespaces(assembly_code: List[str]) -> List[str]:
    return list(map(
        lambda line: line.strip(), assembly_code
    ))


def _parse_empty_lines(assembly_code: List[str]) -> List[str]:
    return list(filter(
        lambda line: line != '', assembly_code
    ))


def _parse_comments(assembly_code: List[str]) -> List[str]:
    return list(map(
        lambda line: line.split(';', 1)[0], assembly_code
    ))


def _extract_section(section_name: str, assembly_code: List[str]) -> List[str]:
    result = []
    for line in assembly_code:
        if line.startswith(f'section .{section_name}'):
            index_after_current_line = assembly_code.index(line) + 1
            for section_line in assembly_code[index_after_current_line:]:
                if section_line.startswith('section'):
                    break
                result.append(section_line)
    return result


def _parse_data_section(assembly_code: List[str]) -> List[Dict[str, str]]:
    parsed_lines = []
    for line in assembly_code:
        split_line = line.split(' ')
        if len(split_line) != 3:
            raise CompilerError(f'"{line}" should contain only 2 spaces: "varName = value"')

        parsed_line = {
            'variable_name': split_line[0],
            'value': split_line[2]
        }

        parsed_lines.append(parsed_line)
    return parsed_lines


def _parse_text_section(assembly_code: List[str]) -> List[Dict[str, str]]:
    parsed_lines = []
    for line in assembly_code:
        split_line = line.replace(', ', ',').split(' ')

        if len(split_line) != 2:
            raise CompilerError(f'"{line}" should contain only 2 statements: "operation ref1, ref2"')

        statements = split_line[1].split(',')

        parsed_line = {
            'operation': split_line[0],
            'first_statement': statements[0],
            'second_statement': statements[1] if len(statements) > 1 else None
        }

        parsed_lines.append(parsed_line)
    return parsed_lines


def _parse_sections(assembly_code: List[str]) -> Dict[str, List[Dict[str, Optional[str]]]]:
    """Returns a dictionary containing the lines separated in sections with the following design:
        dict = {
            'data': [],
            'text': [],
        }
    """
    data_section = _extract_section('data', assembly_code)
    text_section = _extract_section('text', assembly_code)
    result = {
        'data': _parse_data_section(data_section),
        'text': _parse_text_section(text_section),
    }

    return result


def _do_all_parsing(assembly_code: List[str]) -> Dict[str, List[Dict[str, Optional[str]]]]:
    parsed_comments = _parse_comments(assembly_code)
    parsed_newlines = _parse_newline(parsed_comments)
    parsed_whitespaces = _parse_whitespaces(parsed_newlines)
    parsed_empty_lines = _parse_empty_lines(parsed_whitespaces)
    parsed_sections = _parse_sections(parsed_empty_lines)
    return parsed_sections


def get_parsed_code_from_file(path_to_assembly_file: str) -> Dict[str, List[Dict[str, Optional[str]]]]:
    assembly_code = _load_assembly_file(path_to_assembly_file)
    return _do_all_parsing(assembly_code)


if __name__ == '__main__':
    import json

    print(json.dumps(obj=get_parsed_code_from_file('../scripts/count_to_ten.asm'), indent=2))
