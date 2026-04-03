# AI IDE Support

The AI-Native Python template automatically configures AI-powered development tools during project generation.

[← Back to Documentation Index](index.md)


## Automatic Configuration

When you generate a new project, the post-generation hook automatically installs the [Zenable CLI](https://cli.zenable.app) and configures your IDE integrations:

**Installation (if the Zenable CLI is not already installed):**

```bash
curl -fsSL https://cli.zenable.app/install.sh | bash
```

**IDE Configuration:**

Once installed, `zenable install` detects which IDEs and AI assistants you have installed and creates appropriate configuration files for 15+ supported IDEs including Claude Code, Cursor, Windsurf, VS Code, GitHub Copilot, and more.

These configurations are dynamically generated based on your installed IDEs and project settings, and include:

- Project-specific context and guidelines
- Technology stack information
- Code style rules and patterns
- Common tasks and workflows
- Testing requirements and patterns
- Security considerations

For more details on testing configuration and practices, see the [Testing Guide](testing.md).
