from rich.console import Console
from rich.traceback import install
import StatusCheck
install()
c = Console()

builder = StatusCheck.ProjectBuilder()
builder.buildProjectDB()