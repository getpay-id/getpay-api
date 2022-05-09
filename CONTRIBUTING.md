# Contributing Guidelines

Thank you for taking your time to contribute to this project.

## Adding a feature or patch

1. Fork the repository
2. Clone the repository
3. Checkout the `next` branch

```
git checkout -b next origin/next
```

4. Install dev dependencies

```
pipenv install --dev
```

5. Setup pre-commit hooks

```
pre-commit install
```

6. Create a branch for your changes

```
git checkout -b feature/my-feature
```

7. Add and commit your changes

```
git add .
git commit -m "Add my feature"
```

8. Push the branch and make a pull request.

```
git push origin feature/my-feature
```


## Reporting a bug

We use [Issue Tracking](https://github.com/getpay-id/getpay-api/issues) to report bugs/new feature requests.

Before creating an issue, be sure to check for similar issues to avoid duplication. And please add details clearly so we can check it soon.


## Questions

You can ask questions on the [GitHub Discussions](https://github.com/getpay-id/getpay-api/discussions/categories/q-a)
