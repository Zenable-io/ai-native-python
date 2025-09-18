# Development Container Setup

This project includes Dev Container support for VS Code and other compatible editors.

## Quick Start

### Option 1: Using VS Code Dev Containers Extension (Recommended)
1. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Open this project in VS Code
3. Click "Reopen in Container" when prompted, or use Command Palette: `Dev Containers: Reopen in Container`

### Option 2: Attach to Running Container
1. Start the dev container:
   ```bash
   task dev-container
   ```
2. In VS Code, use Command Palette: `Dev Containers: Attach to Running Container`
3. Select the `{{ cookiecutter.project_slug }}-dev` container

### Option 3: Manual Docker Commands
```bash
# Build and start the dev container
task dev-container

# Access the container shell
docker exec -it {{ cookiecutter.project_slug }}-dev bash

# Stop the container when done
task dev-container-stop
```

## Features

The dev container includes:
- Python {{ cookiecutter.python_version }}+ with uv package manager
- All project dependencies (including dev dependencies)
- Git, GitHub CLI, Task, and pre-commit tools
- VS Code extensions for Python development
- Proper volume mounts for live code editing

## Environment

- `DEV_MODE=true` - Installs all development dependencies
- `PYTHONPATH=/workspace/src` - Ensures proper module imports
- Working directory: `/workspace`

## Troubleshooting

If you encounter issues:
1. Ensure Docker is running
2. Check that you have the latest Dev Containers extension
3. Try rebuilding the container: `Dev Containers: Rebuild Container`
4. For manual setup, ensure you run `task init` after container starts