# 📸 Pixel Peep – Challenge Submission Guide

Welcome to the official repository for **Pixel Peep**, a WeCode Community Project!  
This document will guide you through the process of contributing to this challenge using Git and GitHub.

> 🔥 **Top submissions will be selected, and only the winners’ code will be merged into the main Pixel Peep repository under the WeCode organization!**

---

## 🚀 Step 1: Set Up Git & GitHub

### ✅ 1. Install Git  
Download and install Git from the official site:  
👉 https://git-scm.com/downloads

### ✅ 2. Create a GitHub Account  
If you don’t have one yet:  
👉 https://github.com

---

## 🍴 Step 2: Fork the Repository

1. Visit the official Pixel Peep repo:  
   👉 https://github.com/WeCode-Community-Dev/pixel-peep

2. Click the **"Fork"** button on the top-right corner to create your own copy of the repository.

---

## 📥 Step 3: Clone Your Fork

Clone your forked repository to your local machine:

```bash
git clone https://github.com/<your-username>/pixel-peep.git
cd pixel-peep

Replace <your-username> with your GitHub username.

🌿 Step 4: Create a Branch with Your Name

Create a new branch under your name to organize your contributions:

git checkout -b your-name-branch

Example:

git checkout -b anjali-pixelpeep

🔄 Step 5: Keep Your Fork in Sync (Recommended)

Keep your fork up to date with the original repo:

git remote add upstream https://github.com/WeCode-Community-Dev/pixel-peep.git
git fetch upstream
git merge upstream/main

✏️ Step 6: Add Your Solution
	•	Navigate to the appropriate challenge folder.
	•	Upload only the solution file.
	•	File naming format:
<problem-name>.<ext> (e.g., detect-duplicate.py, detect-duplicate.java)

📁 Example Folder Structure:

pixel-peep/
│-- Challenge-1/
│   └── detect-duplicate.py
│-- Challenge-2/
│   └── match-hash.cpp

📤 Step 7: Commit & Push Your Code

Add the file(s):

git add Challenge-1/detect-duplicate.py

Commit with a meaningful message:

git commit -m "Added solution for Detect Duplicate"

Push your branch to your fork:

git push origin your-name-branch

🔁 Step 8: Create a Pull Request
	1.	Go to your forked repository on GitHub.
	2.	Click “Compare & pull request”.
	3.	Select your branch and ensure you’re comparing with main of the original repo.
	4.	Add a clear title and description.
	5.	Click “Create pull request”.

🏆 Winner’s Code Will Be Merged!

✅ The best, original, and correctly working solutions will be selected by reviewers and merged into the official Pixel Peep repository.

Make sure your code:
	•	Works correctly and efficiently
	•	Is clean and well-commented
	•	Follows naming and structure conventions

⚠️ Important Guidelines
	•	✅ Fork the repo first – Do not push directly to the original repo.
	•	✅ Work on a personal branch named after you.
	•	✅ Upload only the relevant solution file(s).
	•	✅ Use clear and concise commit messages.
	•	✅ Keep your fork updated regularly.
	•	✅ Submit a pull request for every challenge.

💬 Need Help?

Reach out to us on the WeCode Community Discord or Forum for any questions or assistance.

Happy Peeping! 👀
Let your code shine — only the best get merged! 🌟

---

Let me know if you want a badge section, table of contents, or any visuals (like a logo or banner) added to this README as well!


