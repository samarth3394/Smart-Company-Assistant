# Nexora CloudSync — Product FAQ

**Product Version:** 4.2  
**Last Updated:** August 15, 2026

---

## General

### What is Nexora CloudSync?

Nexora CloudSync is an **enterprise-grade file synchronization and collaboration platform** that allows teams to store, share, and co-edit documents in real time across all devices. It integrates with Google Workspace, Microsoft 365, Slack, and over 50 other business tools.

### What platforms does CloudSync support?

CloudSync is available on **Windows 10/11**, **macOS 12+**, **Linux (Ubuntu 20.04+, Fedora 38+)**, **iOS 16+**, and **Android 13+**. A full-featured **web application** is accessible at `app.nexora-cloudsync.com`.

### Is there a free tier?

Yes. The **CloudSync Starter** plan is free for up to **5 users** and includes **15 GB of shared storage**, basic file versioning (last 30 days), and community support.

---

## Pricing and Plans

### What plans are available?

| Plan       | Price (per user/month) | Storage     | Key Features                                    |
|------------|------------------------|-------------|-------------------------------------------------|
| Starter    | Free                   | 15 GB       | Basic sync, 30-day versioning                   |
| Pro        | $12                    | 500 GB      | Advanced collaboration, audit logs, SSO          |
| Business   | $28                    | 2 TB        | Admin console, DLP, eDiscovery, 24/7 support     |
| Enterprise | Custom                 | Unlimited   | Dedicated CSM, custom integrations, SLA 99.99%   |

All paid plans include a **14-day free trial** with no credit card required.

### Can I switch plans mid-cycle?

Yes. Upgrades take effect **immediately** and are prorated for the remainder of the billing cycle. Downgrades take effect at the **start of the next billing cycle**. Contact billing@nexora.com or use the Admin Console to change plans.

---

## Security and Compliance

### How is my data protected?

All files are encrypted at rest with **AES-256** and in transit with **TLS 1.3**. CloudSync is SOC 2 Type II certified, GDPR compliant, and HIPAA-eligible (Business and Enterprise plans). Customer data is stored in the region of your choice: **US-East, EU-West, or APAC-Singapore**.

### Does CloudSync support Single Sign-On (SSO)?

Yes. SSO via **SAML 2.0** and **OpenID Connect** is supported on the Pro plan and above. We integrate with Okta, Azure AD, Google Workspace, and OneLogin out of the box.

---

## Troubleshooting

### CloudSync desktop app won't sync — what should I do?

1. Ensure you are running CloudSync **version 4.2 or later** (check via Help → About).
2. Verify your internet connection and firewall settings (port **443** must be open).
3. Clear the local cache: go to **Settings → Advanced → Clear Cache**, then restart the app.
4. If the issue persists, generate a diagnostic bundle (**Help → Generate Diagnostics**) and send it to support@nexora.com.

### File conflicts — how are they resolved?

When two users edit the same file simultaneously offline, CloudSync creates a **conflict copy** named `<filename> (Conflict – <username> – <date>)`. Both versions are preserved, and the users are notified to manually merge changes. Real-time co-editing (available on Pro and above) prevents conflicts entirely by synchronizing edits live.

### What is the maximum file size?

The maximum single-file upload is **15 GB** on all plans. For files larger than 5 GB, we recommend using the **desktop app** or the CloudSync CLI uploader, as the web uploader may time out on slower connections.

---

## Support

### How do I contact support?

- **Starter plan:** Community forum at community.nexora.com
- **Pro plan:** Email support with **24-hour response SLA** at support@nexora.com
- **Business & Enterprise:** 24/7 phone and chat support, plus a dedicated Customer Success Manager

### Where do I find release notes?

Release notes are published at `docs.nexora-cloudsync.com/changelog` after every release. You can also subscribe to the **CloudSync Release Notes** mailing list via the Admin Console.
