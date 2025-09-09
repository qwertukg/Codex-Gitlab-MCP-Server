import click
import uvicorn

from .server import GitlabMCPServer


@click.command()
@click.option("--host", default="0.0.0.0", help="Хост сервера")
@click.option("--port", default=8000, help="Порт сервера")
def main(host: str, port: int) -> None:
    """Запускает MCP сервер."""
    server = GitlabMCPServer()
    uvicorn.run(server.app, host=host, port=port)


if __name__ == "__main__":
    main()
