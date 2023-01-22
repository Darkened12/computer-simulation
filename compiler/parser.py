from typing import List, Dict, Optional

try:
    from .errors import CompilerError
except ImportError:
    from errors import CompilerError


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


def _parse_line(line: str) -> Dict[str, str]:
    split_line = line.replace(', ', ',').split(' ')

    if len(split_line) != 2:
        raise CompilerError(f'"{line}" should contain only 2 statements: "operation ref1, ref2"')

    statements = split_line[1].split(',')

    parsed_line = {
        'operation': split_line[0],
        'first_statement': statements[0],
        'second_statement': statements[1] if len(statements) > 1 else None
    }
    return parsed_line


def _parse_text_section(assembly_code: List[str]) -> List[Dict[str, str]]:
    parsed_lines = []
    for line in assembly_code:
        parsed_line = _parse_line(line)
        parsed_lines.append(parsed_line)
    return parsed_lines


def _parse_subroutines_section(assembly_code: List[str]) -> List[Dict[str, str]]:
    subroutines: List[Dict[str, str]] = []
    current_subroutine: Dict[str, str | List] = {}
    for line in assembly_code:
        if line.endswith(':'):
            if current_subroutine != {}:
                raise CompilerError(f'Missing ret statement on subroutine "{current_subroutine["label"]}"')

            current_subroutine = {'label': f'{line.replace(":", "")}', 'lines': []}
        elif line == 'ret':
            current_subroutine['lines'].append({'operation': 'ret', "first_statement": None, 'second_statement': None})
            subroutines.append(current_subroutine)
            current_subroutine = {}
        else:
            if current_subroutine:
                current_subroutine['lines'].append(_parse_line(line))
            else:
                current_subroutine = {}

    if current_subroutine:
        raise CompilerError(f'Missing ret statement on subroutine "{current_subroutine["label"]}"')

    return subroutines


def _parse_sections(assembly_code: List[str]) -> Dict[str, List[Dict[str, Optional[str]]]]:
    """Returns a dictionary containing the lines separated in sections with the following design:
        dict = {
            'data': [],
            'subroutines': [],
            'text': [],
        }
    """
    data_section = _extract_section('data', assembly_code)
    text_section = _extract_section('text', assembly_code)
    subroutines_section = _extract_section('subroutines', assembly_code)

    parsed_data_section = _parse_data_section(data_section)
    parsed_text_section = _parse_text_section(text_section)
    parsed_subroutines_section = _parse_subroutines_section(subroutines_section)

    result = {
        'data': parsed_data_section,
        'subroutines': parsed_subroutines_section,
        'text': parsed_text_section,
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

    print(json.dumps(obj=get_parsed_code_from_file('../scripts/test.asm'), indent=2))
