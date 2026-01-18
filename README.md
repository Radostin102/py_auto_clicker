# ![py_auto_clicker](./images/title.png)

An auto clicker written in Python.

## Features

- A standard auto clicker
- Minimal, no GUI
- Runs in the background
- Minimized to the system tray

## Usage

Ensure you are in the root directory of the repository and run:

```bash
pip install -r requirements.txt

python ./src/auto_clicker.pyw
```

You can now toggle the auto clicker by pressing `F4`.

To close the program, open the system tray and exit the process.

## Configuration

The configuration file is [`config.toml`](src/config.toml).

**Options:**
- `click_interval`
- `toggle_hotkey`

## Dependencies

- [Python](https://www.python.org/downloads/)
- [Packages](requirements.txt):
  - pynput
  - pystray
  - PIL
