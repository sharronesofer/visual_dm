# Branching Strategy

This document outlines the branching strategy for the Visual DM project.

## Branch Types

- **`main`**: The main production branch. All code in this branch should be stable and deployable.
- **`develop`**: The main development branch. Features are merged here before being released to production.
- **`feature/*`**: Feature branches for new functionality. Should branch from and merge back into `develop`.
- **`bugfix/*`**: Bug fix branches for fixing issues. Should branch from and merge back into the affected branch.
- **`release/*`**: Release branches for preparing releases. Branch from `develop` and merge into both `main` and `develop`.
- **`hotfix/*`**: Hotfix branches for urgent production fixes. Branch from `main` and merge into both `main` and `develop`.

## Workflow

1. Create a new feature branch from `develop`:
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/your-feature-name
   ```

2. Develop your feature, committing changes frequently:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

3. Push your branch to the remote repository:
   ```bash
   git push -u origin feature/your-feature-name
   ```

4. When your feature is complete, create a pull request to merge into `develop`.

5. After code review and approval, your feature will be merged into `develop`.

6. When ready for release, a `release` branch is created from `develop`:
   ```bash
   git checkout develop
   git checkout -b release/1.0.0
   ```

7. After testing, the release is merged into both `main` and `develop`:
   ```bash
   git checkout main
   git merge --no-ff release/1.0.0
   git tag -a v1.0.0 -m "Version 1.0.0"
   git push origin main --tags
   
   git checkout develop
   git merge --no-ff release/1.0.0
   git push origin develop
   ```

## Branch Naming Conventions

- Feature branches: `feature/short-description`
- Bug fix branches: `bugfix/issue-number-description`
- Release branches: `release/version-number`
- Hotfix branches: `hotfix/version-number-description`

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools 