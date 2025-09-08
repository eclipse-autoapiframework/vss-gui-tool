# Introduction 
This repository contains the GUI tool for the selection and addition of signals to the Vehicle Signal Specification (VSS). The tool is used to select signals (data or parameters) from hundreds of signals defined in VSS bassed on the requirements of an application. 

# Getting started 
## Dependencies 
1. The VSS GUI tool runs in Ubuntu (tested in Ubuntu 22.04). 
2. The GUI tool is based on Python (tested in v3.10) and the following libraries: 
    - Tkinter 
    - Anytree
    - Pyyaml 
    - Screeninfo
3. The GUI tool is also dependent on the .vspec files defined in the <a href="https://github.com/COVESA/vehicle_signal_specification">Vehicle Signal Specification</a> repository and the corresponding <a href="https://github.com/COVESA/vss-tools">VSS-tools</a> repository. 

## Structure of the repository 
1. [container](./container) - Contains the dockerfile recipe for the container image that is used to run the necessary scripts. 
2. [scripts](./scripts) - Contains the necessary Python scripts with respect to the GUI tool. 
3. [documentation](./documentation) - Contains the document explaining the features of the GUI tool. 

## Running the script 
1. Update the submodules linked to the repository: `git submodule update --init --recursive`. 
2. Since the GUI tool has been tested upto v4.x of the VSS, navigate to the vss repository located in the [scripts] (./scripts/) folder and checkout to the required version: `git checkout v4.1`. 
3. Update the submodules linked to vss repository: `git submodule update --init --recursive`.
4. Build the container image by running the `build.sh` script in the [container](./container/) folder. 
5. Run the container: `docker run -ti -e DISPLAY=$(hostname).local:0 -it vss_gui:latest`. In case of WSL, ensure that x11 forwarding is enabled and working. 
6. Run the Python `vss_gui.py`script in `/app/gui` folder.  

## Dependencies to other repositories
This tool can be used in combination with application framework: https://github.com/eclipse-autoapiframework/application-framework
