import typer
from options import bcolors, MINIMOVE, MINIWASM, VM_CHOICES, VMChoice
import text
import subprocess
import os
import sys
from rich.progress import BarColumn, Progress, TextColumn, SpinnerColumn
import time
from choice import select_vm, select_network, get_mnemonic
from typing_extensions import Annotated
import json
import constants

app = typer.Typer()


def setup_progress(task_description: str, total: int):
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        task = progress.add_task(f"[cyan]{task_description}...", total=total)
        return progress, task


def install_golang():
    progress, task = setup_progress("Installing Golang 1.22", 100)
    try:
        subprocess.run(
            ["bash", "scripts/install_golang.sh"],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        progress.update(task, advance=100)
        print(bcolors.OKGREEN + "Golang 1.22 installed successfully." + bcolors.ENDC)
    except subprocess.CalledProcessError as e:
        print(bcolors.RED + f"Failed to install Golang 1.22: {e}" + bcolors.ENDC)
        sys.exit(1)


def clone_minitia_repository(vm):
    choice = get_repository_choice(vm)
    repository_url = f"https://github.com/initia-labs/{choice.name}.git"
    print(bcolors.OKGREEN + f"Cloning minitia repository" + bcolors.ENDC)
    clone_repository(repository_url)


def get_repository_choice(vm):
    if vm == VMChoice.MINIMOVE:
        return MINIMOVE
    elif vm == VMChoice.MINIWASM:
        return MINIWASM
    else:
        raise ValueError("Invalid VM choice")


def clone_repository(repository_url):
    try:
        with setup_progress(f"Cloning {repository_url}...", 100) as (
            progress,
            clone_task,
        ):
            subprocess.run(
                ["git", "clone", repository_url],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            progress.update(clone_task, completed=100)
        print(bcolors.OKGREEN + "Repository cloned successfully." + bcolors.ENDC)
    except subprocess.CalledProcessError as e:
        print(bcolors.RED + f"Failed to clone repository: {e}" + bcolors.ENDC)
        sys.exit(1)


def install_postgresql():
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        task = progress.add_task("[cyan]Installing PostgreSQL...", total=100)
        subprocess.run(
            ["bash", "scripts/install_postgresql.sh"],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        progress.update(task, advance=100)
        print(bcolors.OKGREEN + "PostgreSQL installed successfully." + bcolors.ENDC)
        print(bcolors.OKGREEN + "Starting PostgreSQL Service..." + bcolors.ENDC)
        subprocess.run(
            ["bash", "scripts/start_postgresql.sh"],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        print(bcolors.OKGREEN + "PostgreSQL Service Started." + bcolors.ENDC)


def install_docker():
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        task = progress.add_task("[cyan]Installing Docker...", total=100)
        try:
            subprocess.run(
                ["bash", "scripts/install_docker.sh"],
                check=True,
                stdout=subprocess.DEVNULL,
                shell=True,
            )
            progress.update(task, advance=100)
        except subprocess.CalledProcessError as e:
            print(bcolors.RED + f"Failed to install Docker: {e}" + bcolors.ENDC)
            sys.exit(1)
        print(bcolors.OKGREEN + "Docker installed successfully." + bcolors.ENDC)


def install_binary(vm):
    print(vm)
    choice = MINIMOVE
    if vm == VMChoice.MINIMOVE:
        choice = MINIMOVE
    elif vm == VMChoice.MINIWASM:
        choice = MINIWASM

    print(bcolors.OKGREEN + f"Installing minitia binary" + bcolors.ENDC)
    os.chdir(f"{os.getcwd()}/{choice.name}")
    try:
        with Progress(
            TextColumn("[bold blue]{task.description}", justify="right"),
            BarColumn(bar_width=None),
            "[progress.percentage]",
        ) as progress:
            install_task = progress.add_task(
                f"Installing {choice.name} binary...", total=100
            )
            subprocess.run(
                ["make", "install"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            progress.update(install_task, completed=100)
        print(bcolors.OKGREEN + "Installation completed successfully." + bcolors.ENDC)
    except subprocess.CalledProcessError as e:
        print(bcolors.RED + f"Failed to run 'make install': {e}" + bcolors.ENDC)
        sys.exit(1)


def launch_minitia(network, chain_id, denom, sequencer_mnemonic):
    config_data = setup_config_data(chain_id, denom)
    config_path = write_config_to_file(config_data)

    print(f"Minitia configuration file created at {config_path}")
    launch_command = build_launch_command(
        sequencer_mnemonic, network.chain_id, config_path
    )
    try:
        subprocess.run(" ".join(launch_command), shell=True, check=True)
        print("Minitiad launched successfully with the provided configuration.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to launch minitiad: {e}")
        sys.exit(1)


def setup_config_data(chain_id, denom):
    config_data = {
        "l1_config": {
            "rpc_url": constants.L1_RPC_URI,
            "gas_prices": constants.L1_GAS_PRICES,
        },
        "l2_config": {
            "chain_id": chain_id
            or input(
                "Please enter the Minitia Chain ID to use (leave empty to use autogenerated value): "
            ).strip(),
            "denom": denom or constants.DEFAULT_L2_GAS_DENOM,
        },
    }
    if denom == "umin":
        user_denom = input(
            "Please enter the default gas denom for the minitia (leave empty to use default value): "
        ).strip()
        config_data["l2_config"]["denom"] = (
            user_denom if user_denom else constants.DEFAULT_L2_GAS_DENOM
        )
    return config_data


def write_config_to_file(config_data):
    print(config_data)
    config_path = os.path.join(os.getcwd(), "minitia_config.json")
    with open(config_path, "w") as config_file:
        json.dump(config_data, config_file, indent=4)
    return config_path


def build_launch_command(sequencer_mnemonic, chain_id, config_path):
    return [
        "echo",
        f'"{sequencer_mnemonic}"',
        "|",
        "minitiad",
        "launch",
        chain_id,
        "--with-config",
        config_path,
    ]


@app.command()
def init():
    print(bcolors.OKGREEN + text.WELCOME_MESSAGE + bcolors.ENDC)
    install_golang()
    install_postgresql()
    install_docker()


@app.command()
def start(
    vm: Annotated[
        str, typer.Option(help="Minitia VM to deploy. One of 'minimove' or 'miniwasm'")
    ] = "",
    l1: Annotated[
        str,
        typer.Option(
            help="Initia L1 Chain ID to connect to. One of 'mainnet' or 'testnet'"
        ),
    ] = "",
    mnemonic: Annotated[
        str,
        typer.Option(
            help="Mnemonic to use for the minitia bridge executor. This address needs to be funded with gas on the selected L1 chain."
        ),
    ] = "",
    chain_id: Annotated[
        str,
        typer.Option(
            help="Minitia Chain ID to use. If not provided, a random one will be generated."
        ),
    ] = "",
    denom: Annotated[
        str,
        typer.Option(
            help=f"Default gas denom for the minitia. If not provided, {constants.DEFAULT_L2_GAS_DENOM} will be used"
        ),
    ] = constants.DEFAULT_L2_GAS_DENOM,
):
    vm = select_vm(vm)
    network = select_network(l1)
    mnemonic = get_mnemonic(mnemonic)
    clone_minitia_repository(vm)
    install_binary(vm)
    launch_minitia(network, chain_id, denom, mnemonic)


if __name__ == "__main__":
    app()
