# Security Policy for Verbum Minecraft

This document outlines the security policy and practices for the Verbum Minecraft project.

## Supported Versions

Verbum currently supports only the latest release for the targeted Minecraft version.

| Version | Supported |
| --- | --- |
| 0.1.x | ✅ Yes |

## Reporting a Vulnerability

We take the security of Verbum Minecraft seriously. If you believe you have found a security vulnerability, please report it through one of the following channels:

1.  **GitHub Private Vulnerability Reporting:** Please use the "Report a vulnerability" button on the [Security tab](https://github.com/petalofzion/Verbum_Minecraft/security/advisories/new) of this repository. This is our preferred method.
2.  **Email:** You can also report vulnerabilities privately via email to **security@verbum-minecraft.org**.

**Please do not open a public issue for security vulnerabilities.**

### When to Expect a Response

We strive to acknowledge all security reports within **48 hours** and provide a preliminary assessment or update within **7 days**.

## Disclosure Policy

1.  Once a report is received, we will investigate and confirm the vulnerability.
2.  We will work on a fix and coordinate a release.
3.  A security advisory will be published once the fix is available.

## Security Best Practices for Contributors

- **Dependency Management:** Keep dependencies up to date and minimize their use.
- **Code Review:** All PRs, especially in `sim-kernel` or `api`, require thorough security and performance review.
- **Input Validation:** Always validate data from external sources (config files, network packets, save data).
- **Least Privilege:** Use the most restrictive access modifiers and capabilities.
- **No Secrets:** Never hardcode or commit secrets, API keys, or sensitive information.