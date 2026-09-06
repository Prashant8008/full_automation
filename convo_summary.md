# Project Resume Summary: Instagram & Slack Automation Pipeline

This file summarizes the current state of your automation project so you can easily resume when you return.

---

## 1. Current State of the Codebase
*   **Slack Delivery**: Fully operational. The script `send_to_slack_instagram.py` successfully published 4 daily cards (with direct article images scraped from GKToday/SSBCrack) to your Slack channel.
*   **Instagram Publishing**: 
    *   The API token successfully authenticated (no expired token errors).
    *   However, Meta temporarily blocked immediate publishing with an `action is blocked (subcode 2207051)` rate-limit warning.
    *   **Resolution**: Modified `publish_to_instagram.py` to add a **5-minute stagger sleep** (`time.sleep(300)`) between posts to avoid triggering these spam filters. 
    *   *Note*: Wait a few hours for the current block to expire before testing Instagram posts again.

---

## 2. Infrastructure & Always-On Setup
We decided to host the script on an **Oracle Cloud Always Free VM** (4 CPU / 24GB RAM) for 24/7 automation.
*   Refer to the step-by-step setup guide here: **[oracle_setup_guide.md](file:///c:/Users/hp/Downloads/automation/oracle_setup_guide.md)**.
*   It covers connecting via SSH, installing Node/Python/Chrome dependencies, and scheduling the daily run with a system cron job.

---

## 3. Future Roadmap Ideas discussed
1. **Multi-Agent refactoring**:
   *   Dividing tasks among specialized agents: **Geopolitical Researcher Agent** (sourcing), **Copywriter Agent** (caption & layout planning), and **Operations Agent** (screenshot compilation and publishing).
   *   Adding a feedback loop where the Ops agent can tell the Copywriter to fix/shorten text if it overflows the card.
2. **SaaS Conversion**:
   *   Building a web app dashboard where users connect their social media accounts via OAuth, configure their branding guidelines (logo, colors, fonts), and let the multi-agent crew autonomously manage their accounts end-to-end.

---

*See you when you return!*
