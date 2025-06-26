# Frequently Asked Questions

## Release Workflow Issues

### Q: Why is my release workflow failing with permission errors?

**A:** The release workflow requires the GitHub Actions bot to have permission to push commits to the main branch. This is necessary because semantic-release creates a commit to update version numbers in files.

#### Solution:

1. **For GitHub.com repositories:**
   - Go to Settings → Actions → General
   - Under "Workflow permissions", select "Read and write permissions"
   - Check "Allow GitHub Actions to create and approve pull requests"
   - Click "Save"

2. **For GitHub Enterprise repositories:**
   - Ensure the GitHub Actions bot (`github-actions[bot]`) has write access to the repository
   - Check branch protection rules for the main branch:
     - Go to Settings → Branches
     - Edit the protection rule for `main`
     - Under "Restrict who can push to matching branches", ensure GitHub Actions is allowed
     - Alternatively, add a bypass for the GitHub Actions bot

3. **For organizations with restricted permissions:**
   - The organization may need to explicitly grant the GitHub Actions app permission to push
   - Contact your organization administrators if default permissions are restricted

### Q: Why does semantic-release fail with "no commits to release"?

**A:** Semantic-release uses conventional commits to determine the next version. If there are no commits following the conventional commit format since the last release, it won't create a new release.

Ensure your commits follow the format:
- `feat:` for new features (triggers minor version bump)
- `fix:` for bug fixes (triggers patch version bump)
- `BREAKING CHANGE:` in the commit body (triggers major version bump)
- Other types like `docs:`, `chore:`, `style:` don't trigger releases

### Q: Can I manually specify the version number?

**A:** No, the workflow is designed to automatically determine the version based on conventional commits. This ensures consistent versioning across all projects. If you need a specific version, ensure your commits indicate the appropriate change level.

## Local Development

### Q: How do I test releases locally?

**A:** You can test the release process locally using:
```bash
task release -- --no-push --no-vcs-release
```

This will:
- Calculate the next version based on commits
- Update version files
- Generate changelog entries (if configured)
- But NOT push to git or create GitHub releases

### Q: How do I manually trigger a release?

**A:** Releases are triggered through GitHub Actions:
1. Go to Actions → Release workflow
2. Click "Run workflow"
3. Select the branch (usually `main`)
4. Click "Run workflow"

The workflow will automatically determine the version based on commits since the last release.
