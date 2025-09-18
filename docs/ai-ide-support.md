# AI IDE Support

The AI-Native Python template automatically configures AI-powered development tools during project generation.

[← Back to Documentation Index](index.md)


## Automatic Configuration

When you generate a new project, the post-generation hook automatically detects which IDEs and AI assistants you have installed and creates appropriate configuration files:

- Model Context Protocol (MCP) configuration for [Zenable](https://zenable.io) and other MCP servers (if supported tools are detected)
- IDE-specific configuration files based on what's installed (Claude, GitHub Copilot, Cursor, etc.)
- Project-specific context and guidelines tailored to your project

These configurations are dynamically generated based on your installed IDEs and project settings, and include:

- Project-specific context and guidelines
- Technology stack information
- Code style rules and patterns
- Common tasks and workflows
- Testing requirements and patterns
- Security considerations

For more details on testing configuration and practices, see the [Testing Guide](testing.md).
