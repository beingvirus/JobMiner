# Contributing to JobMiner 🎉

First off, thank you for considering a contribution to **JobMiner**! Your help is invaluable in making this project better for everyone. We're excited to welcome you to our community. 🚀

This project is **Hacktoberfest-friendly** 💻🍂. We encourage you to pick up issues, suggest improvements, or open a pull request.

---

## 🚀 How to Contribute

To ensure a smooth workflow, please follow these steps.

### 1. Fork the Repository

First, you'll need your own copy of the repository. Click the **Fork** button on the top-right corner of the [main repository page](https://github.com/beingvirus/JobMiner). This will create a copy of the project in your own GitHub account.

### 2. Clone Your Fork

Now, clone your forked repository to your local machine. Replace `YOUR_USERNAME` with your actual GitHub username.

```bash
git clone https://github.com/YOUR_USERNAME/JobMiner.git
cd JobMiner
````

### 3\. Add an Upstream Remote

To keep your fork synced with the original project, you need to add the original repository as an "upstream" remote.

```bash
git remote add upstream https://github.com/beingvirus/JobMiner.git
```

You can verify that the remote was added correctly by running:

```bash
git remote -v
```

### 4\. Keep Your Fork Synced

Before you start making changes, pull the latest code from the upstream repository to ensure your local version is up-to-date.

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

### 5\. Create a New Branch

It's best practice to create a new branch for each feature or bug fix. This keeps your changes organized. Use a descriptive name for your branch.

```bash
# For a new feature:
git checkout -b feature/your-awesome-feature

# For a bug fix:
git checkout -b fix/a-tricky-bug
```

### 6\. Make Your Changes

Now you're ready to code\! Feel free to:

  * Add a new feature
  * Fix a bug
  * Improve documentation
  * Add tests
  * Optimize existing code
  * Add scrapers for new job portals

### 7\. Commit and Push Your Changes

Once you're happy with your changes, commit them with a clear and descriptive message.

```bash
# Stage your changes
git add .

# Commit your changes
git commit -m "feat: Add a scraper for a new job portal"

# Push the changes to your fork
git push origin feature/your-awesome-feature
```

### 8\. Open a Pull Request

Finally, go to your forked repository on GitHub. You'll see a prompt to create a **Pull Request**. Click on it, provide a clear title and description for your changes, and submit it for review. We'll get back to you as soon as possible\!

-----

## ✅ Contribution Guidelines

  * **Code Style:** Please follow **PEP 8** guidelines for Python code.
  * **Commit Messages:** Write clear, concise, and descriptive commit messages.
  * **Pull Requests:** Keep your pull requests small and focused on a single issue or feature.
  * **Documentation:** If you add a new feature, please update the documentation accordingly.
  * **Testing:** Ensure your code works as expected before submitting a PR.

-----

## 📜 License

By contributing, you agree that your contributions will be licensed under the **MIT License**.

✨ Thank you for being a part of the JobMiner and open-source community\!
Happy coding and Happy Hacktoberfest\! 🎃👩‍💻👨‍💻
