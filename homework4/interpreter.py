from config import CMDS
from pandas import DataFrame

def get_command_parts(f, first_byte):
    command = int.from_bytes(first_byte) >> 3
    parts = []
    for key in CMDS:
        cmd = CMDS[key]
        if cmd['number'] == command:
            all_command = int.from_bytes(first_byte) << ((cmd['size'] - 1) * 8)
            next_bytes = int.from_bytes(f.read(cmd['size'] - 1))
            all_command |= next_bytes

            shift = 0
            for i in range(len(cmd['layout'])):
                shift += cmd['layout'][i]
                parts.append(
                    (all_command >> (cmd['size'] * 8 - shift)) & (2 ** (cmd['layout'][i]) - 1)
                )
    return parts


def interpret(input_file, result_file):

    memory = [0] * (2 ** 28)
    registers = [0] * (2 ** 5)

    with open(input_file, 'rb') as f:
        first_byte = f.read(1)
        while first_byte != b'':
            parts = get_command_parts(f, first_byte)
            if len(parts):
                if parts[0] == CMDS["CONST"]['number']:
                    _, b, c = parts
                    registers[b] = c
                if parts[0] == CMDS["READ"]['number']:
                    _, b, c = parts
                    registers[b] = memory[c]
                if parts[0] == CMDS["WRITE"]['number']:
                    _, b, c = parts
                    memory[b] = registers[c]
                if parts[0] == CMDS["OR"]['number']:
                    _, b, c, d = parts
                    registers[c] = memory[registers[b]] | registers[d]
            else:
                raise Exception("Unknown command")
            first_byte = f.read(1)

    df = DataFrame(columns=['Register value'], data=registers)
    df.to_csv(result_file)


if __name__ == "__main__":
    interpret("p.bin", "out.csv")