# 🔐 Security Policy

## Supported Versions

We actively maintain the latest version of the **JobMiner** project. Please ensure you're always using the most recent release to benefit from the latest features and security updates.

| Version | Supported |
|---------|-----------|
| latest  | ✅        |
| older   | ❌        |

---

## 📢 Reporting a Vulnerability

If you discover a security vulnerability in this project, **do not open an issue directly on GitHub**.

Instead, please follow these steps:

1. **Contact us directly** via email.

2. Provide a clear and detailed description of the issue, including:
   - Steps to reproduce the vulnerability
   - The impact it could have
   - Any recommended fixes (if available)
3. Allow us a reasonable time to investigate and fix the vulnerability before disclosing it publicly.

---

## 🔐 Security Best Practices

To help keep the JobMiner app and its users secure, please follow these best practices during development and deployment:

- Never share sensitive credentials, API keys, or database passwords openly in public repositories.

- Use environment variables (e.g., via .env files with python-dotenv) to securely manage secrets and tokens.

- Always run the latest supported versions of dependencies and Python itself to benefit from security patches.

- Perform regular security audits using tools such as bandit for Python code security analysis and safety to detect vulnerable dependencies.

- Implement proper error handling to avoid exposing sensitive information in logs or error messages.

- Use proxies and rotate IP addresses when scraping to avoid IP blocking and reduce chances of detection.

- Use realistic user-agent strings and consider headless browser approaches to mimic human browsing behavior.

---

## 🛡️ Scope of Security

This security policy applies to:

- The source code in this repository
- Configuration files
- Dependencies defined in `requirements.txt`

**Note:** Issues related to third-party services or APIs used by the app (e.g., payment gateways, external APIs) should be reported to those service providers.

---

## 🤝 Responsible Disclosure

We appreciate responsible disclosure of any vulnerability. All security reports will be acknowledged and investigated promptly. We are committed to maintaining a secure and safe environment for all contributors and users.

Thank you for helping keep **JobMiner** secure! 🍽️