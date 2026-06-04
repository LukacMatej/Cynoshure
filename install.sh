#!/bin/bash

/home/mates/Python/Cynoshure/.venv/bin/pyinstaller --onefile --name cyno main.py
sudo cp dist/cyno /usr/local/bin/cyno
