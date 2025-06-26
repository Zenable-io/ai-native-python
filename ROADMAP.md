# AI Native Python - Roadmap

This document outlines future improvements and enhancements for the ai-native-python project.

## Ideas

### 1. Add Policy as Code

- Add [digestabot](https://github.com/chainguard-dev/digestabot) and pin all actions
- Add [zizmor](https://github.com/zizmorcore/zizmor)
- Ensure the python version is in line throughout the repo; python_version in the refurb config with .python-version, with the default in Dockerfile, etc.
- Ensure that the correct task steps exist in Taskfile.yml

### 2. Improve flexibility/usability

- Keep the public yes/no but split out a CodeQL yes/no (default to yes; secure by default but it may error if insufficient licensing)
- Improve the docs around releasing and rulesets/branch protections

### 3. Improve project health checks

- Automated security checks
- Code quality metrics
- Dependency health monitoring

### 4. Support additional runtimes

- Dev container configuration / local testing
- Lambda image runtime support in AWS
- Docker Compose examples
- Cloud-native deployments/IaC (ECS, EKS, AKS, GKE)

### 5. AI-powered project customization

- Natural language project specification
- Intelligent dependency selection
- Code scaffold generation based on requirements

### 6. Integration with more pipelines

- Cloud provider integrations (AWS, GCP, Azure)
- CI/CD platform integrations (GitLab, ADO, bitbucket)

### 7. Project analytics and insights

- Development velocity metrics
- Dependency update compliance
- Security posture tracking

## Technical Debt to Address

### Documentation

- Add architecture decision records (ADRs)
- Create video tutorials
- Improve troubleshooting guides

## Community Feedback Ideas

We welcome community feedback and contributions. Some areas where we'd especially appreciate input:

- Additional project templates needed
- Integration requirements with other tools
- Security and compliance features
- Developer experience improvements

## Contributing

If you're interested in contributing to any of these roadmap items, please:

1. Open an issue to discuss the feature
2. Submit a pull request with your implementation
3. Update this roadmap as items are completed

For more information, see [CONTRIBUTING.md](.github/CONTRIBUTING.md)
