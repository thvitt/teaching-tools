from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from multiprocessing import Process, Queue
from subprocess import run
import os
import shlex
import logging
from typing import Any, Optional
from pathlib import Path
import typer

logger = logging.getLogger(__name__)
app = typer.Typer()


def http_server(queue: Queue, start_port: int, serve_dir: Optional[str]):
    class LoggingRequestHandler(SimpleHTTPRequestHandler):
        next_level: int = logging.DEBUG

        def log_error(self, format: str, *args: Any) -> None:
            self.next_level = logging.ERROR
            return logger.error(format, *args)

        def log_message(self, format: str, *args: Any) -> None:
            result = logger.log(self.next_level, format, *args)
            self.next_level = logging.DEBUG
            return result

    try:
        if serve_dir:
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
            logger.info("Serving from %s at http://localhost:%d/", os.getcwd(), port)
            server.serve_forever()
    except OSError as e:
        logger.error("Cannot start server: %s", e)


@app.command()
def main(
    cmd: list[str],
    start_port: int = 8000,
    serve_dir: Optional[Path] = None,
    verbose: bool = False,
    shell: bool = False,
):
    """
    Run a command while serving a directory via HTTP.

    This command first starts a simple HTTP server on a free port,
    runs the given command and finally shuts down the HTTP server.

    The server will serve the directory given with --serve-dir
    (current directory by default) and all its subdirectories.
    It will find a free TCP port that is at least start_port to
    run the server. If --verbose, the server will output an
    access log and some more details.

    The remaining arguments specify the command to run and its
    arguments. The special string {port} will be replaced with
    the port number used by the server. If --shell is given,
    the system shell will be used to run the command, in this
    case only one non-option argument should be given.

    The exit code will be passed on from the command.
    """
    logging.basicConfig(level=logging.INFO if verbose else logging.WARNING)
    queue = Queue()
    proc = Process(target=http_server, args=(queue, start_port, serve_dir))
    proc.start()
    port = queue.get()
    filled_in_cmd = [arg.replace("{port}", str(port)) for arg in cmd]
    logger.info("Running %s", shlex.join(filled_in_cmd))
    try:
        completed_process = run(filled_in_cmd, shell=shell)
    finally:
        proc.terminate()
    return completed_process.returncode
