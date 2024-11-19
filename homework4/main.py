import click
from assembler import assemble  # Функция assemble из пакета assembler
from interpreter import interpret  # Функция interpret из пакета interpreter

@click.group()
def cli():
    """Основная группа команд CLI."""
    pass

@click.command("assemble")
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.argument('log_file', type=click.Path())
def assemble_command(input_file, output_file, log_file):
    """Собирает файл с помощью функции assemble."""
    try:
        assemble(input_file, output_file, log_file)
        click.echo(f"Сборка завершена. Результат сохранен в {output_file}. Лог: {log_file}.")
    except Exception as e:
        click.echo(f"Ошибка при сборке: {e}", err=True)

@click.command("interpret")
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('result_file', type=click.Path())
def interpret_command(input_file, result_file):
    """Интерпретирует файл с помощью функции interpret."""
    try:
        interpret(input_file, result_file)
        click.echo(f"Интерпретация завершена. Результат сохранен в {result_file}.")
    except Exception as e:
        click.echo(f"Ошибка при интерпретации: {e}", err=True)

# Добавляем команды в основную группу CLI
cli.add_command(assemble_command)
cli.add_command(interpret_command)

if __name__ == '__main__':
    cli()
