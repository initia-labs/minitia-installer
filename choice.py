from options import VMChoice, NetworkChoice, bcolors, TESTNET
import sys


def select_vm(vm: str):
    # Check if setup is specified in args
    if vm != "":
        if vm == "minimove":
            return VMChoice.MINIMOVE
        elif vm == "miniwasm":
            return VMChoice.MINIWASM
        else:
            print(
                bcolors.RED
                + f"Invalid setup {vm}. Please choose a valid setup.\n"
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


def select_network(network):
    """
    Selects a network based on user input or command-line arguments.

    Returns:
        chosen_network (NetworkChoice): The chosen network, either MAINNET or TESTNET.

    Raises:
        SystemExit: If an invalid network is specified or the user chooses to exit the program.
    """

    # Check if network is specified in args
    if network != "":
        if network == TESTNET.chain_id:
            choice = NetworkChoice.TESTNET
        else:
            print(
                bcolors.RED
                + f"Invalid network {network}. Please choose a valid network."
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


def get_mnemonic(mnemonic):
    if mnemonic != "":
        return mnemonic
    print(
        "You need to prepare a L1 token funded account for IBC and bridge setup. This account will be used as Bridge Executor."
    )
    print("Please enter the sequencer_mnemonic of the account:")
    sequencer_mnemonic = input()
    return sequencer_mnemonic
