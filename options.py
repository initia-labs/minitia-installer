from enum import Enum
import os


DEFAULT_MINITIA_HOME = os.path.expanduser("~/.minitiad")
DEFAULT_MONIKER = "initia"

NETWORK_CHOICES = ["initiation-1"]
VM_CHOICES = ["minimove", "miniwasm"]

MINIWASM_VERSION = "0.2.14"
MINIMOVE_VERSION = "0.2.12"

# Choices
class NetworkChoice(str, Enum):
    TESTNET = "1"


class VMChoice(str, Enum):
    MINIMOVE = "1"
    MINIWASM = "2"


class Answer(str, Enum):
    YES = "1"
    NO = "2"


class Network:
    def __init__(self, chain_id, version, rpc_node, lcd_node):
        self.chain_id = chain_id
        self.version = version
        self.lcd_node = lcd_node
        self.rpc_node = rpc_node


class Minitia:
    def __init__(self, name, vm, version):
        self.name = name
        self.vm = vm
        self.version = version


TESTNET = Network(
    "initiation-1",
    "0.2.12",
    "https://rpc-initia.01node.com:443",
    "https://lcd.initiation-1.initia.xyz",
)

MINIMOVE = Minitia("minimove", "minimove", MINIMOVE_VERSION)
MINIWASM = Minitia("miniwasm", "miniwasm", MINIWASM_VERSION)


class bcolors:
    OKGREEN = "\033[92m"
    RED = "\033[91m"
    ENDC = "\033[33m"
    PURPLE = "\033[95m"
