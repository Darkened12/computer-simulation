def get_byte_array_from_integer(number: int, size: int) -> str:
    bit_length = f'0{size}b'
    return f'{number:{bit_length}}'
