import sys
import os
from cx_Freeze import setup, Executable

# Add the path to the src directory
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["os", "arcade"],
    "includes": ["views.menu", "views.game", "views.pause", "data.constants"],
    "include_files": [
        ("resources/data", "resources/data"),
        ("resources/fonts", "resources/fonts"),
        ("resources/maps", "resources/maps"),
        ("resources/sounds", "resources/sounds"),
        ("resources/spritesheets", "resources/spritesheets"),
        ("resources/textures", "resources/textures"),
    ],
    "excludes": []
}

# Base is set to None for console application
base = None

# Define the main executable
executables = [
    Executable(
        script="src/main.py",
        base=base,
        target_name="Hungry Kitty Uprising",
        icon=None
    )
]

# Setup cx_Freeze
setup(
    name="Hungry Kitty Uprising",
    version="1.0",
    description="Feed the cats.",
    options={"build_exe": build_exe_options},
    executables=executables
)
