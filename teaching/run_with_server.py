from ast import Param
import logging
import os
import shlex
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from multiprocessing import Process, Queue
from pathlib import Path
from subprocess import run
from typing import Annotated, Any, override

from cyclopts import App, Parameter
from cyclopts.types import ExistingDirectory
from rich.logging import RichHandler
from sqlalchemy import alias

logger = logging.getLogger(__name__)
app = App()


def http_server(queue: Queue, start_port: int, serve_dir: Path):
    class LoggingRequestHandler(SimpleHTTPRequestHandler):
        next_level: int = logging.DEBUG

        @override
        def log_error(self, format: str, *args: Any) -> None:  # pyright: ignore[reportExplicitAny]
            self.next_level = logging.ERROR
            return logger.error(format, *args)

        @override
        def log_message(self, format: str, *args: Any) -> None:  # pyright: ignore[reportExplicitAny]
            result = logger.log(self.next_level, format, *args)
            self.next_level = logging.DEBUG
            return result

    try:
        os.chdir(serve_dir)
        port = start_port
        while True:
            try:
                server = ThreadingHTTPServer(("", port), LoggingRequestHandler)
                break
            except OSError:
                port += 1
        with server:
            queue.put(port)
            logger.info("Serving from %s at http://localhost:%d/", Path().cwd(), port)
            server.serve_forever()
    except OSError as e:
        logger.error("Cannot start server: %s", e)


@app.default()
def main(
    *cmd: str,
    start_port: Annotated[int, Parameter(alias="-p")] = 8000,
    serve_dir: Annotated[ExistingDirectory, Parameter(alias="-d")] = Path(),  # pyright: ignore[reportCallInDefaultInitializer]
    verbose: Annotated[bool, Parameter(alias="-v", negative=False)] = False,
    shell: Annotated[bool, Parameter(alias="-s", negative=False)] = False,
    browser: Annotated[bool, Parameter(alias="-b", negative=False)] = False,
):
    """
    Serve a directory via http while optionally running a command.

    Args:
        cmd: if present, run this command line while serving the directory,
             and terminate the server when the command has finished. The
             special argument {port} will be replaced by the actual port
             the content is served. If missing, display a prompt and
             terminate the server when a newline is entered.
        start_port: the TCP port for the webserver. If this port cannot be
                    bound, the port number will be increased until we find
                    a port actually available.
        serve_dir: the directory to serve.
        verbose: output access logs and additional messages.
        shell: expand the command line via the configured shell.
        browser: open (and focus) a browser window
    """
    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING,
        handlers=[RichHandler(show_path=False)],
        format="%(message)s",
    )
    queue = Queue()  # type: Queue[int]
    proc = Process(target=http_server, args=(queue, start_port, serve_dir))
    proc.start()
    port = queue.get()
    filled_in_cmd = [arg.replace("{port}", str(port)) for arg in cmd]
    url = f"http://localhost:{port}/"
    if browser:
        webbrowser.open(url)
    try:
        if cmd:
            logger.info("Running %s", shlex.join(filled_in_cmd))
            completed_process = run(filled_in_cmd, shell=shell)
            return completed_process.returncode
        else:
            app.console.input(
                f"Running server for {serve_dir} on port [bold]{port}[/bold], visit [link={url}]{url}[/link]\nPress return to stop."
            )
    finally:
        proc.terminate()
