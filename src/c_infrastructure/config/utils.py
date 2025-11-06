from pathlib import Path


def get_project_root() -> Path:
    """
    Finds the project root by searching upwards for the 'pyproject.toml' file.

    This approach is robust against changes in the directory structure.

    Returns:
        The Path object for the project's root directory.

    Raises:
        FileNotFoundError: If the 'pyproject.toml' file cannot be found.
    """
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise FileNotFoundError("Could not find project root. Make sure 'pyproject.toml' exists in the root directory.")
