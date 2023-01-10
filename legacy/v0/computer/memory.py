from base import Binary, BinarySet, NOT


class GatedLatch:
    def __init__(self, data_in: Binary):
        self.data_input = data_in
        self.write_enable = Binary(0)
        self._data_output = Binary(0)

    def __repr__(self):
        return f'{self._data_output}'

    def update(self):
        and1 = self.data_input & self.write_enable
        and2 = NOT(self.data_input) & self.write_enable
        and2 = Binary(and2)

        or1 = and1 | self._data_output
        and3 = or1 & NOT(and2)

        self._data_output = and3

    @property
    def data_output(self):
        return self._data_output


class Registry:
    def __init__(self, size: int = 8):
        self.size = size
        self._memory_cells = [GatedLatch(Binary(0)) for n in range(size)]

    def __repr__(self):
        return ''.join([str(bit) for bit in self.data_output])

    @property
    def memory_cells(self) -> list[GatedLatch]:
        return list(reversed(self._memory_cells))

    @property
    def data_input(self) -> BinarySet:
        return BinarySet(array=[cell.data_input for cell in self.memory_cells], size=self.size)

    @data_input.setter
    def data_input(self, binary_set: BinarySet):
        if len(binary_set) != self.size:
            raise NotImplementedError

        for cell, bit in zip(reversed(self.memory_cells), binary_set):
            cell.data_input = bit

    @property
    def data_output(self) -> list[Binary]:
        return [cell.data_output for cell in self.memory_cells]

    @property
    def write_enable(self):
        return self._memory_cells[0].write_enable

    @write_enable.setter
    def write_enable(self, binary: Binary):
        for cell in self._memory_cells:
            cell.write_enable = binary

    def update(self):
        for cell in self.memory_cells:
            cell.update()


def _debug_gated_latch():
    gl = GatedLatch(Binary(1))

    gl.write_enable = Binary(1)
    gl.update()
    print(gl.data_output)

    gl.data_input = Binary(0)
    gl.write_enable = Binary(1)
    gl.update()
    print(gl.data_output)


def _debug_registry():
    def _debugger(new_entry: str = ''):
        string = f'REGISTRY input: {registry.data_input}, output: {registry.data_output}, write_enable: {registry.write_enable}'
        print(string + f', memory_cells: {registry.memory_cells}' + new_entry)

    registry = Registry(size=4)
    _debugger()

    data_input = BinarySet(array=[0, 1, 0, 1], size=4)
    registry.data_input = data_input
    _debugger(f', data_input SET {data_input}')

    registry.update()
    _debugger(', registry.update()')

    registry.write_enable = 1
    _debugger(', write_enable SET 1')

    registry.update()
    _debugger(', registry.update()')

    registry.write_enable = 0
    _debugger(', write_enable SET 0')

    data_input = BinarySet(size=4)
    registry.data_input = data_input
    _debugger(f', data_input SET {data_input}')

    registry.update()
    _debugger(', registry.update()')

    registry.write_enable = 1
    _debugger(', write_enable SET 1')

    registry.update()
    _debugger(', registry.update()')


if __name__ == '__main__':
    _debug_registry()
