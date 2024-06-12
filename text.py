WELCOME_MESSAGE = """

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

DOCKER_SETUP_SCRIPT = """
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
"""

DOCKER_INSTALL_SCRIPT = """
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
"""
