import subprocess
import sys
from progress import setup_progress
from options import bcolors

def install_docker():
    progress, task = setup_progress("Installing Docker...", 100)
    try:
        subprocess.run(
            ["bash", "scripts/install_docker.sh"],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        progress.update(task, advance=100)
    except subprocess.CalledProcessError as e:
        print(bcolors.RED + f"Failed to install Docker: {e}" + bcolors.ENDC)
        sys.exit(1)
    print(bcolors.OKGREEN + "Docker installed successfully." + bcolors.ENDC)

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

def install_postgresql():
    progress, task = setup_progress("Installing PostgreSQL...", 100)
    try:
        subprocess.run(
            ["bash", "scripts/install_postgresql.sh"],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        progress.update(task, advance=50)
        print(bcolors.OKGREEN + "PostgreSQL installed successfully." + bcolors.ENDC)
        
        print(bcolors.OKGREEN + "Starting PostgreSQL Service..." + bcolors.ENDC)
        subprocess.run(
            ["bash", "scripts/start_postgresql.sh"],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        progress.update(task, advance=50)
        print(bcolors.OKGREEN + "PostgreSQL Service Started." + bcolors.ENDC)
    except subprocess.CalledProcessError as e:
        print(bcolors.RED + f"Failed to install or start PostgreSQL: {e}" + bcolors.ENDC)
        sys.exit(1)