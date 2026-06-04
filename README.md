# Cynoshure

Cynoshure is an interactive, terminal-based SSH Manager built with Python and the [Textual](https://textual.textualize.io/) framework. It provides a clean, user-friendly interface to manage your SSH connections, configurations, history, and favorites directly from your terminal.

## Features

- **Interactive TUI:** Navigate your SSH configurations and connections using an intuitive tree-based sidebar.
- **Quick Connect:** Easily connect to servers on the fly without needing to configure them beforehand.
- **Session Management:** Save your frequently accessed servers as favorites (Sessions) for quick access.
- **Connection History:** Automatically tracks your recent SSH connections so you can easily reconnect.
- **Global Configurations:** Configure default SSH settings such as:
  - Default Username
  - SSH Key Paths
  - X11 Forwarding (`-X`)
  - Jump Hosts (`-J`)
  - Port Forwarding (`-L`)

## Prerequisites

- Python 3.8+

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/Cynoshure.git
   cd Cynoshure
   ```

2. (Optional but recommended) Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Standalone Executable (Optional)

If you want to install Cynoshure as a standalone executable available system-wide, you can use the included `install.sh` script. This script bundles the application using PyInstaller and installs it to `/usr/local/bin/cyno`.

Make sure you have `pyinstaller` installed, then run the script:
```bash
pip install pyinstaller
./install.sh
```

## Usage

Start the application by running the main Python script:

```bash
./main.py
```

Navigate the interface using your mouse or keyboard arrow keys. Press `d` to toggle dark/light mode and `q` to quit the application.