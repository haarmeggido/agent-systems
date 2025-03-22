# Project for Agent Systems Course at AGH University

[![Python Package Testing](https://github.com/haarmeggido/agent-systems/actions/workflows/python-package-test.yml/badge.svg)](https://github.com/haarmeggido/agent-systems/actions/workflows/python-package-test.yml)

Implementation of an Autonomous intersection model that is solved by agents using reinforcement learning technics.

### Authors

- Miłosz Góralczyk
- Dominik Breksa

### Setup guide

Prerequisites needed to install the project:
- Python 3.12.9 or higher
- Unix System

Here I will show the steps needed to set up the repository so that you can then make use of this repository.

1. Clone the repository from GitHub servers to your local machine:

   ```bash
   git clone git@github.com:haarmeggido/agent-systems.git
   cd ./agent-systems
   ```
   
2. Set up the package manager of your choice i.e. conda, venv or poetry. Here is an example command to create a virtual environment.

   ```bash
   python -m venv .venv
   ```

3. Start the setup script located at the ***./scripts/*** folder. The following script requires Bash shell to be installed on your machine. It will install the python package associated with this project (***ainter***) to the newly created python environment.

    ```bash
    chmod +x ./scripts/setup.sh
    ./scripts/setup.sh
    ```

### Project Consumption

##### Testing the project

To test the project we can use the provided script at the ***./scripts/*** folder. Usage of the script is shown below:

```bash
chmod +x ./scripts/test.sh
./scripts/test.sh
```

After that, the coverage report database will be located at the root of the project (***.coverage*** file).