# Installation
To install TTSV
```bash
git clone --recurse-submodules https://github.com/Netajam/TTSV.git
```
## Required Dependencies
In order for zonos to work install espeak-ng
```bash
!apt install -y espeak-ng
```
```bash
!touch TTSV/zonosp/__init__.py
!touch TTSV/zonosp/zonos/__init__.py
```
Create symlink to detect zonos as a module

```bash
 !ln -s zonosp/zonos zonos
```
Install the depencies for ttsv module
```bash
cd TTSV && pip install -e .
```
Install depencencies for zonos
# Running
## How to run

### **Run Everything**
```sh
python main.py
```

### **Run Only a Specific Step**
```sh
python main.py --step 2  # Merge output files
python main.py --step 4  # Upload to YouTube
```

### **Run from a Specific Step Onward**
```sh
python main.py --from-step 1  # Start from text processing
python main.py --from-step 3  # Start from video generation
```

## Running on Google Colab
You will need to set up your secrets. Use the same names as in the .env.template file. If you want to upload your video on youtube.
# Dependencies

Zonos package installed as a git submodule

