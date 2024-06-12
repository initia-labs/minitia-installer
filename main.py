import typer
from typing import Optional
from options import bcolors, MINIMOVE, MINIWASM, VM_CHOICES, VMChoice
import text
import subprocess
import os
import sys
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
    SpinnerColumn
)
import time
from choice import select_vm, select_network, get_mnemonic
from typing_extensions import Annotated
import json

app = typer.Typer()

def update_apt():
  with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
    task = progress.add_task("[cyan]Updating APT...", total=100)
    subprocess.run(["sudo", "apt", "update"], check=True, stdout=subprocess.DEVNULL)

def setup_progress(task_description: str, total: int):
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task(f"[cyan]{task_description}...", total=total)
        return progress, task

def install_golang():
    progress, task = setup_progress("Installing Golang 1.22", 100)
    try:
        subprocess.run(["sudo", "add-apt-repository", "ppa:longsleep/golang-backports", "-y"], check=True, stdout=subprocess.DEVNULL)
        progress.update(task, advance=30)
        subprocess.run(["sudo", "apt", "install", "golang-go", "-y"], check=True, stdout=subprocess.DEVNULL)
        progress.update(task, advance=70)
        print(bcolors.OKGREEN + "Golang 1.22 installed successfully." + bcolors.ENDC)
    except subprocess.CalledProcessError as e:
        print(bcolors.RED + f"Failed to install Golang 1.22: {e}" + bcolors.ENDC)
        sys.exit(1)

def clone_minitia_repository(vm):
    choice = MINIMOVE
    if vm == VMChoice.MINIMOVE:
        choice = MINIMOVE
    elif vm == VMChoice.MINIWASM:
        choice = MINIWASM
    repository_url = f"https://github.com/initia-labs/{choice.name}.git"
    print(bcolors.OKGREEN + f"Cloning minitia repository" + bcolors.ENDC)
    try:
        with Progress(
    TextColumn("[bold blue]{task.description}", justify="right"),
    BarColumn(bar_width=None),
    "[progress.percentage]",
) as progress:
            clone_task = progress.add_task(f"Cloning initia-labs/{choice.name}...", total=100)
            subprocess.run(["git", "clone", repository_url], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            progress.update(clone_task, completed=100)
        print(bcolors.OKGREEN + "Repository cloned successfully." + bcolors.ENDC)
    except subprocess.CalledProcessError as e:
        print(bcolors.RED + f"Failed to clone repository: {e}" + bcolors.ENDC)
        sys.exit(1)

def install_postgresql():
  with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
    task = progress.add_task("[cyan]Installing PostgreSQL...", total=100)
    subprocess.run(["sudo", "apt", "install", "postgresql", "postgresql-contrib", "-y"], check=True, stdout=subprocess.DEVNULL)
    progress.update(task, advance=100)
    print(bcolors.OKGREEN + "PostgreSQL installed successfully." + bcolors.ENDC)
    print(bcolors.OKGREEN + "Starting PostgreSQL Service..." + bcolors.ENDC)
    subprocess.run(["sudo", "systemctl", "start", "postgresql"], check=True, stdout=subprocess.DEVNULL)
    print(bcolors.OKGREEN + "PostgreSQL Service Started." + bcolors.ENDC)

def install_docker():
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("[cyan]Installing Docker...", total=100)
        try:
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "ca-certificates", "curl", "-y"], check=True)
            subprocess.run(["sudo", "install", "-m", "0755", "-d", "/etc/apt/keyrings"], check=True)
            subprocess.run(["sudo", "curl", "-fsSL", "https://download.docker.com/linux/ubuntu/gpg", "-o", "/etc/apt/keyrings/docker.asc"], check=True)
            subprocess.run(["sudo", "chmod", "a+r", "/etc/apt/keyrings/docker.asc"], check=True)
            subprocess.run([
                "echo",
                "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable",
                "|",
                "sudo", "tee", "/etc/apt/sources.list.d/docker.list"
            ], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "docker-ce", "docker-ce-cli", "containerd.io", "docker-buildx-plugin", "docker-compose-plugin", "-y"], check=True)
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
            install_task = progress.add_task(f"Installing {choice.name} binary...", total=100)
            subprocess.run(["make", "install"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            progress.update(install_task, completed=100)
        print(bcolors.OKGREEN + "Installation completed successfully." + bcolors.ENDC)
    except subprocess.CalledProcessError as e:
        print(bcolors.RED + f"Failed to run 'make install': {e}" + bcolors.ENDC)
        sys.exit(1)

def launch_minitia(network, sequencer_mnemonic):
    config_data = {
        "l1_config": {
            "rpc_url": "https://rpc.t.initia.bh.rocks:443",
            "gas_prices": "0.15move/944f8dd8dc49f96c25fea9849f16436dcfa6d564eec802f3ef7f8b3ea85368ff",
        }
    }

    config_path = os.path.join(os.getcwd(), "config.json")
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

@app.command()
def init():
    print(
        bcolors.OKGREEN
        + text.WELCOME_MESSAGE
        + bcolors.ENDC
    )
    # update_apt()
    # install_golang()
    install_postgresql()
    install_docker()

@app.command()
def start(vm: Annotated[str, typer.Option(help="Minitia VM to deploy. One of 'minimove' or 'miniwasm'")] = "",
    l1: Annotated[str, typer.Option(help="Initia L1 Chain ID to connect to. One of 'mainnet' or 'testnet'")] = "",
    mnemonic: Annotated[str, typer.Option(help="Mnemonic to use for the minitia bridge executor. This address needs to be funded with gas on the selected L1 chain.")] = ""):
    vm = select_vm(vm)
    network = select_network(l1)
    mnemonic = get_mnemonic(mnemonic)
    clone_minitia_repository(vm)
    install_binary(vm)
    launch_minitia(network, mnemonic)



if __name__ == "__main__":
    app()
