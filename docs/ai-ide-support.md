# AI IDE Support

The AI-Native Python template includes configuration files to work seamlessly with AI-powered development tools.

[← Back to Documentation Index](index.md)


## Tool-agnostic configurations

### .mcp.json

Model Context Protocol configuration pre-set to integrate with:

- [Zenable](https://zenable.io)'s MCP server
- [Context7](https://context7.com/)'s MCP server

## Specific IDE configurations

### Claude Code

Every generated project includes a `CLAUDE.md` file with:

- Project-specific context and guidelines
- Technology stack information
- Code style rules and patterns
- Common tasks and workflows

### GitHub Copilot Configuration

The template includes `.github/copilot-instructions.md` with:

- Project-specific context for GitHub Copilot
- Code conventions and patterns
- Testing requirements and workflow
- Security considerations
- Common code patterns and examples
- Task automation commands

### Cursor IDE Configuration

The template includes `.cursor/rules/` directory with:

- `project.mdc`: Always-active rules with project info, tech stack, and key commands
- `testing.mdc`: Auto-attached rules for test files with testing guidelines and patterns

For more details on testing configuration and practices, see the [Testing Guide](testing.md).
