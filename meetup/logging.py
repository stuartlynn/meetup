from rich.console import Console

console = Console()


def logInfo(message: str) -> None:
    console.print(message, style="green")


def logError(message: str) -> None:
    console.print(message, style="red")


def logWarning(message: str) -> None:
    console.print(message, style="purple")
