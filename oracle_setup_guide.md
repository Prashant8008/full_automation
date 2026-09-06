# Oracle Cloud VM Setup Guide for Automation Pipeline

This guide walks you through provisioning an "Always Free" Oracle Cloud VM, installing dependencies, copying your codebase, and scheduling the daily pipeline to run automatically.

---

## Step 1: Provision the VM on Oracle Cloud
1. Sign up/Log in to the [Oracle Cloud Console](https://cloud.oracle.com/).
2. Click **Create a VM instance**.
3. Configure the VM:
   * **Placement**: Default is fine.
   * **Image**: Click *Edit* and select **Canonical Ubuntu** (version 22.04 or 24.04).
   * **Shape**: Click *Edit* -> Select **Ampere (ARM)** -> Choose **VM.Standard.A1.Flex**.
     * Allocate **2 to 4 OCPUs** and **12 to 24 GB RAM** (all within the free limit).
   * **Networking**: Choose *Create a new Virtual Cloud Network (VCN)* and check *Assign a public IPv4 address*.
   * **SSH Keys**: Click **Save private key** to download the `.key` (or `.pem`) file. **You need this file to connect to your server!**
4. Click **Create** at the bottom. Wait 2-3 minutes for the instance status to turn green (**Running**).
5. Copy the **Public IP Address** of your instance.

---

## Step 2: Connect to your VM via SSH
Open PowerShell or command prompt on your computer and connect to the VM using the private key you downloaded:

```bash
ssh -i /path/to/your/ssh-key.key ubuntu@<YOUR_VM_PUBLIC_IP>
```
*(Replace `/path/to/your/ssh-key.key` with the path to the downloaded key, and `<YOUR_VM_PUBLIC_IP>` with the public IP you copied).*

---

## Step 3: Install Core Dependencies
Once you are connected to the Ubuntu server, run the following commands to update the system and install Node.js, Python, and Git:

```bash
# Update package list and system packages
sudo apt update && sudo apt upgrade -y

# Install Python3, pip, and Git
sudo apt install python3 python3-pip python3-venv git -y

# Install Node.js (Version 20+)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

Verify the installations:
```bash
python3 --version
node -v
npm -v
```

---

## Step 4: Install Google Chrome & Puppeteer Dependencies
Because Puppeteer needs to render HTML cards and take screenshots, you must install Chromium and its required Linux graphics libraries on the headless server:

```bash
# Install Chromium browser
sudo apt install chromium-browser -y

# Install standard GUI/fonts libraries needed for headless rendering
sudo apt install -y libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2 libpango-1.0-0 libcairo2 fonts-liberation
```

---

## Step 5: Clone the Repository & Configure Credentials
1. Clone your project repository to the server:
   ```bash
   git clone <YOUR_GIT_REPOSITORY_URL> automation
   cd automation/daily-instagram-posts-pipeline
   ```
2. Create your `.env` file on the server:
   ```bash
   nano .env
   ```
3. Copy-paste your configurations into the file:
   ```env
   # API Keys
   GEMINI_API_KEY=your_gemini_api_key_here
   FACEBOOK_ACCESS_TOKEN=EAAbZBp0...
   INSTAGRAM_BUSINESS_ACCOUNT_ID=...
   SLACK_BOT_TOKEN=xoxb-...
   SLACK_CHANNEL_ID=...

   # Configurations
   DRY_RUN=false
   INSTAGRAM_DELAY_MINUTES=60
   ```
   Press `Ctrl + O` then `Enter` to save, and `Ctrl + X` to exit the nano editor.

4. Install the Python and Node.js packages:
   ```bash
   # Install python requirements
   pip3 install -r requirements.txt

   # Install node modules
   npm install
   ```

---

## Step 6: Test the Run
Run the pipeline manually to verify everything compiles and renders correctly:

```bash
# Generate the daily plan & visual assets
python3 plan_daily_posts.py
python3 fetch_card_images.py
python3 generate_instagram_posts.py
node build_instagram_visuals.cjs

# Verify the output images are created in output/
ls -lh output/
```

---

## Step 7: Schedule the Daily Pipeline (Cron Job)
To make the pipeline run automatically every day at a specific time (e.g., 9:00 AM server time), use the Linux `cron` scheduler:

1. Open the cron editor:
   ```bash
   crontab -e
   ```
   *(Select `1` to open in nano if asked)*.

2. Add a line at the bottom of the file (e.g., to run daily at 9:00 AM UTC):
   ```text
   0 9 * * * cd /home/ubuntu/automation/daily-instagram-posts-pipeline && python3 plan_daily_posts.py && python3 fetch_card_images.py && python3 generate_instagram_posts.py && node build_instagram_visuals.cjs && python3 publish_to_instagram.py >> run.log 2>&1
   ```
3. Save and exit.

Your pipeline is now fully automated and will run every single day on your free Oracle Cloud instance!
