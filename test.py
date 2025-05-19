from rich.console import Console
from rich.traceback import install
import StatusCheck
install()
c = Console()

scanner = StatusCheck.Scanner()
scanner.modifySettings()