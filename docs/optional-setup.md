# Optional Setup Guide

This guide covers optional setup steps and configurations for the AI-Native Python template.

[← Back to Documentation Index](index.md)

## Grant Installation (License Compliance)

If you'd like to support license file checking locally, you will need to install `grant` and put it in your `PATH`. See [their installation
guide](https://github.com/anchore/grant?tab=readme-ov-file#installation) for more details

## SSH Configuration for Cookiecutter

If you prefer to use SSH instead of HTTPS for cloning the template, you can use the SSH URL.

### Prerequisites

1. SSH key configured with GitHub:

   ```bash
   # Check for existing SSH keys
   ls -la ~/.ssh

   # Generate new SSH key if needed
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. Add SSH key to GitHub:

   ```bash
   # Copy public key
   cat ~/.ssh/id_ed25519.pub
   # Add to GitHub: Settings -> SSH and GPG keys
   ```

3. Test SSH connection:

   ```bash
   ssh -T git@github.com
   ```

### Using SSH with Cookiecutter

```bash
# Use SSH URL instead of HTTPS
uvx --with gitpython cookiecutter git+ssh://git@github.com/zenable-io/ai-native-python.git
```

## Environment Variable Configuration

Set environment variables before running cookiecutter to modify hook behavior (see the [Hooks Guide](hooks.md#configuration)).
