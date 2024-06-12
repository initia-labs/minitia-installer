import os
import sys
import argparse
import subprocess
import platform
import random
import textwrap
import urllib.request as urlrq
import ssl
import json
import tempfile
from enum import Enum

DEFAULT_MINITIA_HOME = os.path.expanduser("~/.minitiad")
DEFAULT_MONIKER = "initia"

NETWORK_CHOICES = ["initiation-1"]
VM_CHOICES = ["minimove", "miniwasm"]

MINIWASM_VERSION = "0.2.14"
MINIMOVE_VERSION = "0.2.12"

parser = argparse.ArgumentParser(description="Minitia Installer")

parser.add_argument(
    "--home",
    type=str,
    help=f"Minitia installation location",
    default=os.getcwd(),
)

parser.add_argument(
    "-m",
    "--moniker",
    type=str,
    help="Moniker name for the node (Default: 'osmosis')",
)

parser.add_argument(
    "-v", "--verbose", action="store_true", help="Enable verbose output", dest="verbose"
)

parser.add_argument(
    "-o",
    "--overwrite",
    action="store_true",
    help="Overwrite existing Osmosis home and binary without prompt",
    dest="overwrite",
)

parser.add_argument(
    "-vm",
    "--vm",
    type=str,
    choices=VM_CHOICES,
    help=f"Minitia VM to use: {VM_CHOICES})",
)

parser.add_argument(
    "-t",
    "--network",
    type=str,
    choices=NETWORK_CHOICES,
    help=f"Network to join: {NETWORK_CHOICES})",
)

parser.add_argument(
    "--binary_path",
    type=str,
    help=f"Path where to download the binary",
    default=os.getcwd(),
)

parser.add_argument(
    "-s", "--service", action="store_true", help="Setup systemd service (Linux only)"
)

args = parser.parse_args()


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

# Terminal utils


class bcolors:
    OKGREEN = "\033[92m"
    RED = "\033[91m"
    ENDC = "\033[33m"
    PURPLE = "\033[95m"


def clear_screen():
    os.system("clear")


def welcome_message():
    print(
        bcolors.OKGREEN
        + """

 .----------------.  .-----------------. .----------------.  .----------------.  .----------------.  .----------------. 
| .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |
| |     _____    | || | ____  _____  | || |     _____    | || |  _________   | || |     _____    | || |      __      | |
| |    |_   _|   | || ||_   \|_   _| | || |    |_   _|   | || | |  _   _  |  | || |    |_   _|   | || |     /  \     | |
| |      | |     | || |  |   \ | |   | || |      | |     | || | |_/ | | \_|  | || |      | |     | || |    / /\ \    | |
| |      | |     | || |  | |\ \| |   | || |      | |     | || |     | |      | || |      | |     | || |   / ____ \   | |
| |     _| |_    | || | _| |_\   |_  | || |     _| |_    | || |    _| |_     | || |     _| |_    | || | _/ /    \ \_ | |
| |    |_____|   | || ||_____|\____| | || |    |_____|   | || |   |_____|    | || |    |_____|   | || ||____|  |____|| |
| |              | || |              | || |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------' 


Welcome to the Minitia node installer!


For more information, please visit https://docs.initia.xyz
"""
        + bcolors.ENDC
    )


def client_complete_message(osmosis_home):
    print(
        bcolors.OKGREEN
        + """
✨ Congratulations! You have successfully completed setting up your minitia!! ✨
"""
        + bcolors.ENDC
    )

    print(
        "🪢 Try running: "
        + bcolors.OKGREEN
        + f"minitiad status --home {osmosis_home}"
        + bcolors.ENDC
    )
    print()


def select_vm():
    # Check if setup is specified in args
    if args.vm:
        if args.vm == "minimove":
            return VMChoice.MINIMOVE
        elif args.vm == "miniwasm":
            return VMChoice.MINIWASM
        else:
            print(
                bcolors.RED
                + f"Invalid setup {args.vm}. Please choose a valid setup.\n"
                + bcolors.ENDC
            )
            sys.exit(1)
    else:
        print(
            bcolors.OKGREEN
            + """
Please choose the desired minitia VM:

    1) minimove   - setup a minimove minitia with MoveVM support
    2) miniwasm   - setup a miniwasm minitia with CosmWasm support

💡 You can select the installation using the --vm flag.
            """
            + bcolors.ENDC
        )

        while True:
            choice = input(
                "Enter your choice (1 for minimove, 2 for miniwasm), or 'exit' to quit: "
            ).strip()

            if choice.lower() == "exit":
                print("Exiting the program...")
                sys.exit(0)

            if choice == "1":
                return VMChoice.MINIMOVE
            elif choice == "2":
                return VMChoice.MINIWASM
            else:
                print(
                    bcolors.RED
                    + "Invalid input. Please choose a valid option. Accepted values: [1, 2]\n"
                    + bcolors.ENDC
                )


def select_network():
    """
    Selects a network based on user input or command-line arguments.

    Returns:
        chosen_network (NetworkChoice): The chosen network, either MAINNET or TESTNET.

    Raises:
        SystemExit: If an invalid network is specified or the user chooses to exit the program.
    """

    # Check if network is specified in args
    if args.network:
        if args.network == TESTNET.chain_id:
            choice = NetworkChoice.TESTNET
        else:
            print(
                bcolors.RED
                + f"Invalid network {args.network}. Please choose a valid network."
                + bcolors.ENDC
            )
            sys.exit(1)

    # If not, ask the user to choose a network
    else:
        print(
            bcolors.OKGREEN
            + f"""
Please choose the desired network:

    1) Testnet ({TESTNET.chain_id})

💡 You can select the network using the --network flag.
"""
            + bcolors.ENDC
        )

        while True:
            choice = input("Enter your choice, or 'exit' to quit: ").strip()

            if choice.lower() == "exit":
                print("Exiting the program...")
                sys.exit(0)

            if choice not in [NetworkChoice.TESTNET]:
                print(
                    bcolors.RED
                    + "Invalid input. Please choose a valid option. Accepted values: [ 1 , 2] \n"
                    + bcolors.ENDC
                )
            else:
                break
    network = TESTNET
    if choice == NetworkChoice.TESTNET:
        network = TESTNET
    return network


def clone_repository(vm):
    """
    Downloads the binary for the specified network based on the operating system and architecture.

    Args:
        network (NetworkChoice): The network type, either MAINNET or TESTNET.

    Raises:
        SystemExit: If the binary download URL is not available for the current operating system and architecture.
    """
    """ binary_path = os.path.join(args.binary_path, "minitiad")

    if not args.overwrite:
        # Check if osmosisd is already installed
        try:
            subprocess.run(
                [binary_path, "version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            print(
                "minitiad is already installed at "
                + bcolors.OKGREEN
                + f"{binary_path}"
                + bcolors.ENDC
            )
            while True:
                choice = (
                    input(
                        "Do you want to skip the cloning or overwrite the repository? (skip/overwrite): "
                    )
                    .strip()
                    .lower()
                )
                if choice == "skip":
                    print("Skipping download.")
                    return
                elif choice == "overwrite":
                    print("Proceeding with overwrite.")
                    break
                else:
                    print("Invalid input. Please enter 'skip' or 'overwrite'.")
        except subprocess.CalledProcessError:
            print("osmosisd is not installed. Proceeding with download.") """

    choice = MINIMOVE

    if vm == VMChoice.MINIMOVE:
        choice = MINIMOVE
    elif vm == VMChoice.MINIWASM:
        choice = MINIWASM
    binary_url = f"https://github.com/initia-labs/{choice.name}.git"

    try:
        print("Cloning " + bcolors.PURPLE + f"{choice.name}" + bcolors.ENDC, end="\n\n")
        print("from " + bcolors.OKGREEN + f"{binary_url}" + bcolors.ENDC, end=" ")
        print("to " + bcolors.OKGREEN + f"{args.binary_path}" + bcolors.ENDC)
        print()
        print(
            bcolors.OKGREEN
            + "💡 You can change the path using --binary_path"
            + bcolors.ENDC
        )

        subprocess.run(["git", "clone", binary_url], check=True)
        print("Minitia repository cloned successfully.")

    except subprocess.CalledProcessError as e:
        print(e)
        print("Failed to clone the minitia repository.")
        sys.exit(1)

    print()


def install_binary(vm):
    choice = MINIMOVE
    if vm == VMChoice.MINIMOVE:
        choice = MINIMOVE
    elif vm == VMChoice.MINIWASM:
        choice = MINIWASM

    print(f"Installing {choice.name} binary")
    if args.home:
        os.chdir(f"{args.home}/{choice.name}")
        try:
            subprocess.run(["make", "install"], check=True)
            print("Installation completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to run 'make install': {e}")
            sys.exit(1)
    else:
        print("No home directory specified. Skipping 'make install'.")


def launch_minitia(network, sequencer_mnemonic):
    config_data = {
        "l1_config": {
            "rpc_url": "http://34.126.129.53:26657",
            "gas_prices": "0.15move/944f8dd8dc49f96c25fea9849f16436dcfa6d564eec802f3ef7f8b3ea85368ff",
        }
    }

    config_path = os.path.join(args.home, "config.json")
    with open(config_path, "w") as config_file:
        json.dump(config_data, config_file, indent=4)

    print(f"Minitia configuration file created at {config_path}")
    command = [
        "echo",
        f'"{sequencer_mnemonic}"',
        "|",
        "minitiad",
        "launch",
        network.chain_id,
        "--with-config",
        config_path,
    ]
    try:
        subprocess.run(" ".join(command), shell=True, check=True)
        print("Minitiad launched successfully with the provided configuration.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to launch minitiad: {e}")
        sys.exit(1)


def create_minitia_service():
    username = subprocess.check_output("whoami").decode().strip()
    home_directory = subprocess.check_output(["getent", "passwd", username]).decode().split(':')[5]

    service_content = f"""
[Unit]
Description=Minitia Node Daemon
After=network-online.target

[Service]
Environment="DAEMON_NAME=minitiad"
Environment="DAEMON_HOME={home_directory}/.minitiad"
Environment="DAEMON_RESTART_AFTER_UPGRADE=true"
Environment="DAEMON_ALLOW_DOWNLOAD_BINARIES=false"
Environment="UNSAFE_SKIP_BACKUP=true"
User={username}
ExecStart={home_directory}/go/bin/minitiad start
Restart=always
RestartSec=3
LimitNOFILE=4096

[Install]
WantedBy=multi-user.target
"""

    service_file_path = "/etc/systemd/system/minitiad.service"

    try:
        subprocess.run(["sudo", "tee", service_file_path], input=service_content.encode(), check=True)
        print("Systemd service file created successfully.")
    except PermissionError:
        print("Permission denied: You need to run this script as root to create systemd service files.")
    except Exception as e:
        print(f"An error occurred: {e}")
    # Enabling and starting the systemd service for minitiad
    try:
        subprocess.run(["sudo", "systemctl", "enable", "minitiad"], check=True)
        print("minitiad service enabled successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to enable minitiad service: {e}")

    try:
        subprocess.run(["sudo", "systemctl", "start", "minitiad"], check=True)
        print("minitiad service started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to start minitiad service: {e}")


def start_minitia():
    print("Starting Minitiad...")
    minitiad_command = [
        "minitiad",
        "start",
    ]
    try:
        subprocess.run(minitiad_command, check=True)
        print("Minitiad started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to start minitiad: {e}")
        sys.exit(1)


def get_mnemonic():
    print(
        "You need to prepare a L1 token funded account for IBC and bridge setup. This account will be used as Bridge Executor."
    )
    print("Please enter the sequencer_mnemonic of the account:")
    sequencer_mnemonic = input()
    return sequencer_mnemonic


def collect_minitia_config():
    config_file_path = os.path.join(
        os.path.expanduser("~"), ".minitia", "artifacts", "config.json"
    )
    try:
        with open(config_file_path, "r") as file:
            config_data = json.load(file)
            l2_chain_id = config_data["l2_config"]["chain_id"]
            print(f"Loaded L2 chain ID: {l2_chain_id}")
    except FileNotFoundError:
        print("Error: config.json file not found.")
        sys.exit(1)
    except KeyError:
        print("Error: 'chain_id' not found in L2 configuration.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: config.json is not a valid JSON file.")
        sys.exit(1)
    return l2_chain_id

def install_opinit():
    print("Cloning OPinit-bots repository...")
    try:
        subprocess.run(["git", "clone", "https://github.com/initia-labs/OPinit-bots.git", "--quiet"], check=True)
        print("Repository cloned successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to clone repository: {e}")
        sys.exit(1)

    print("Changing directory to OPinit-bots...")
    os.chdir("OPinit-bots")

    print("Installing dependencies via npm...")
    try:
        subprocess.run(["npm", "install", "--loglevel", "silent"], check=True)
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        sys.exit(1)

def setup_bridge_executor():
    pass

def setup_output_submitter():
    pass

def setup_batch_submitter():
    pass

def main():
    welcome_message()
    chosen_vm = select_vm()
    network = select_network()
    sequencer_mnemonic = get_mnemonic()
    clone_repository(chosen_vm)
    install_binary(chosen_vm)
    launch_minitia(network, sequencer_mnemonic)
    l2_chain_id = collect_minitia_config()
    create_minitia_service()
    install_opinit()
    setup_bridge_executor()

main()
