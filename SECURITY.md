# Security

This project manages local skill files. It does not request or store credentials, configure accounts, or contact a remote service during install, validation, or uninstall.

## Reporting a vulnerability

Do not put secrets, tokens, private paths, or exploit details in a public issue. Use the repository host's private security-reporting channel when the public repository is enabled. Until then, contact the maintainer privately with the smallest reproducible description and avoid sending credentials or private runtime data.

Please include the affected file or command, the observed impact, safe reproduction steps, and whether the issue changes an owned file outside the requested target. We will acknowledge receipt, assess scope, and document a fix or mitigation without publishing sensitive data.

## Safe handling

Review lifecycle targets before using `--replace` or uninstall. The scripts fail closed on symlink components, checksum changes, malformed manifests, and lock conflicts. Never bypass those checks by copying a private runtime directory into a public issue or patch.
