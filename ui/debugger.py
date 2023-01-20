import tkinter as tk

from computer.computer import Computer
from computer.status import StatusEmitter


def run(ram_data):
    def generate_label(text, register):
        label = tk.Label(root, text=f'{text}: 00000000 (0)')
        emitter.on_cpu_update(lambda event, cpu: label.config(
            text=f'{text}: {register}'))
        label.pack()

    root = tk.Tk()
    root.title("8 bit computer")
    root.geometry("300x400")

    pc = Computer()
    pc.ram.from_list(ram_data)
    emitter = StatusEmitter(pc.cpu)
    phase_generator = pc.cpu.next_phase()

    phase = tk.Label(root, text=f'current_phase: None')
    emitter.on_cpu_update(lambda event, cpu: phase.config(text=f'current_phase: {event}'))
    phase.pack()


    generate_label('program_counter_register', pc.cpu.program_counter_register)
    generate_label('instruction_register', pc.cpu.instruction_register)
    generate_label('address_register', pc.cpu.address_register)
    generate_label('stack_pointer', pc.cpu.stack_pointer)

    generate_label('ax', pc.cpu.register_A)
    generate_label('bx', pc.cpu.register_B)
    generate_label('cx', pc.cpu.register_C)
    generate_label('dx', pc.cpu.register_D)

    generate_label('acc', pc.cpu.accumulator_register)
    generate_label('sr', pc.cpu.status_register)

    button = tk.Button(root, text='Next Phase', command=lambda: next(phase_generator))
    button.pack()

    try:
        root.mainloop()
    except Exception as err:
        root.destroy()
        root.quit()
        raise err
