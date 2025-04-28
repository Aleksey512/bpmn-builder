import sys

import uvicorn

from application.api.main import create_api_conf


def runserver(*args: str) -> None:
    """Запуск сервера API через uvicorn API."""
    uvicorn.run(**create_api_conf())


def main() -> None:
    """Главная точка входа."""
    COMMANDS = {
        "runserver": runserver,
    }

    if len(sys.argv) < 2:
        print(f"Укажите команду: {list(COMMANDS.keys())}")
        sys.exit(1)

    command_name = sys.argv[1]
    func = COMMANDS.get(command_name)

    if not func:
        print(
            f"Неизвестная команда: {command_name}. "
            f"Используйте одну из {list(COMMANDS.keys())}"
        )
        raise RuntimeError("Unknown command")

    func(*sys.argv[1:])


if __name__ == "__main__":
    main()
