#!/bin/bash
path=$PWD
$path/.venv/bin/pyinstaller --onefile --name cyno main.py
sudo cp $path/dist/cyno /usr/local/bin/cyno
