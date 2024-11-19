"""
Assembler commands examples

CONST B=17 C=747
READ B=28 C=219
WRITE B=744 C=25
OR B=23 C=0 D=25
"""
from config import CMDS
from pandas import DataFrame


def bytes_to_hex_string(byte_data):
    hex_string = ', '.join(f"0x{byte:02X}" for byte in byte_data)
    return hex_string

def assemble(input_file, output_file, log_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    instructions = []
    instructions_strings = []
    for line in lines:
        if line.startswith("//"):
            continue
        command = line.split(" ")[0]
        params = [int(param.split("=")[1]) for param in line.split(" ")[1:]]

        if command not in CMDS:
            raise Exception("Unknown command")

        command_data = CMDS[command]
        shift = 8 * command_data['size']
        parts = [command_data['number'], *params]
        instruction = 0
        for i in range(len(parts)):
            shift -= command_data['layout'][i]
            if parts[i] >= 2**(command_data['layout'][i]):
                raise Exception(f"Too big number, cmd: {command}, part: {i}, number: {parts[i]}")
            instruction |= (parts[i] << shift)

        instruction_bytes = instruction.to_bytes(command_data['size'], byteorder='big')
        instructions.append(instruction_bytes)
        letters = ["A", "B", "C", "D", "E", "F"]
        instructions_strings.append(", ".join(f"{letters[i]}={parts[i]}" for i in range(len(parts))))

    df = DataFrame(columns=['line'], data=instructions_strings)
    df.to_csv(log_file)

    with open(output_file, 'wb') as f:
        for instruction in instructions:
            f.write(instruction)


if __name__ == "__main__":
    assemble(
        "in.txt",
        "p.bin",
        "log.csv"
    )