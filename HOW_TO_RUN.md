# How to Run the App - Simple Guide

## For Complete Beginners

### What's a Virtual Environment?

Think of a virtual environment like a separate "workspace" for this project. It keeps all the Python packages (libraries) needed for this app separate from other Python projects on your computer.

**Why it matters**: Without it, you might have conflicting package versions between different projects.

---

## Step-by-Step Instructions

### 1. Open Terminal

On Mac:
- Press `Command + Space`
- Type "Terminal"
- Press Enter

### 2. Navigate to Your Project

Copy and paste this command:

```bash
cd /Users/jordanzapakin/Documents/code/Sixfold/claims-risk-analyzer
```

Press Enter.

**What this does**: `cd` means "change directory" - it moves you into the project folder.

### 3. Activate the Virtual Environment

Copy and paste this command:

```bash
source .venv/bin/activate
```

Press Enter.

**What you'll see**: Your terminal prompt will change to show `(.venv)` at the beginning, like this:

```
(.venv) jordanzapakin@Jordans-MacBook-Air claims-risk-analyzer %
```

**What this does**: This "activates" the virtual environment, telling your terminal to use the Python packages installed specifically for this project.

### 4. Run the App

Copy and paste this command:

```bash
streamlit run app.py
```

Press Enter.

**What you'll see**:
- Some startup messages
- A URL that says `Local URL: http://localhost:8501`
- Your default web browser should open automatically

**If browser doesn't open**: Just copy that URL (`http://localhost:8501`) and paste it into your web browser.

### 5. Use the App

Once the browser opens:
1. Click "Use minimal sample data" button OR
2. Upload one of your CSV files (insurance_dataset.csv or data_synthetic.csv)
3. Explore the data quality features in the sidebar!

---

## Stopping the App

To stop the app:
1. Go back to Terminal
2. Press `Control + C` (hold Control key, then press C)
3. The app will stop

---

## One-Command Quick Start

If you want to do everything in one step, copy all of this:

```bash
cd /Users/jordanzapakin/Documents/code/Sixfold/claims-risk-analyzer && source .venv/bin/activate && streamlit run app.py
```

This does steps 2, 3, and 4 all at once!

---

## Understanding That Error You Saw

The error you got earlier:

```
NameError: name 'age_method' is not defined
```

**What happened**: The code was trying to use variables (`age_method`, `income_method`) before they were created. It's like trying to use your phone before you bought it.

**What I fixed**: I moved the code that USES those variables to come AFTER the code that CREATES them. Now they're in the right order.

**Think of it like cooking**:
- ❌ Bad: Try to make a sandwich → realize you need bread → buy bread
- ✅ Good: Buy bread → make a sandwich

---

## What Changed in Your App

Here's what we added:

### 1. **Data Quality Validation** (New!)
- **Where**: Sidebar → "Data Quality" section
- **What it does**:
  - Detects ages outside normal range (like ages over 100)
  - Detects incomes that look wrong
  - Gives you options: fix them, remove them, or leave them

### 2. **Schema Normalization** (New!)
- **What it does**: Makes different datasets work with the same app
- **Example**:
  - Dataset 1 calls it "Income"
  - Dataset 2 calls it "Income Level"
  - Your app treats both as "annual_income"
- **Why it matters**: You can use multiple datasets without changing code

### 3. **Visual Feedback** (New!)
- **Where**: Main page, "Data Quality Report" card
- **What it shows**:
  - How many values were cleaned
  - What values were used to replace bad data
  - Total impact on your dataset

---

## Troubleshooting

### "Command not found: streamlit"

**Fix**: Make sure you activated the virtual environment first:
```bash
source .venv/bin/activate
```

You should see `(.venv)` at the start of your terminal prompt.

### "No such file or directory"

**Fix**: Make sure you're in the right folder:
```bash
cd /Users/jordanzapakin/Documents/code/Sixfold/claims-risk-analyzer
```

Then try again.

### App won't open in browser

**Manual fix**:
1. Look for this line in Terminal: `Local URL: http://localhost:8501`
2. Copy that URL
3. Open your web browser
4. Paste the URL in the address bar
5. Press Enter

### Port already in use

**Fix**: If you see an error about port 8501 already being used:
1. Press `Control + C` to stop any running apps
2. Try running the app again

Or use a different port:
```bash
streamlit run app.py --server.port 8502
```

---

## File Locations (For Reference)

Your datasets are here:
- `/Users/jordanzapakin/Documents/code/Sixfold/insurance_dataset.csv`
- `/Users/jordanzapakin/Documents/code/Sixfold/data_synthetic.csv`

Your project files are here:
- `/Users/jordanzapakin/Documents/code/Sixfold/claims-risk-analyzer/app.py` (main app)
- `/Users/jordanzapakin/Documents/code/Sixfold/claims-risk-analyzer/helpers.py` (data processing)

---

## Quick Commands Cheat Sheet

| What You Want | Command |
|---------------|---------|
| Go to project folder | `cd /Users/jordanzapakin/Documents/code/Sixfold/claims-risk-analyzer` |
| Activate virtual env | `source .venv/bin/activate` |
| Run the app | `streamlit run app.py` |
| Stop the app | Press `Control + C` |
| Deactivate virtual env | `deactivate` |
| Do everything at once | `cd /Users/jordanzapakin/Documents/code/Sixfold/claims-risk-analyzer && source .venv/bin/activate && streamlit run app.py` |

---

## What's Next?

After you get the app running:

1. **Try the sample data first** - Click "Use minimal sample data" to see how it works
2. **Upload insurance_dataset.csv** - This one has data quality issues to demonstrate
3. **Play with Data Quality settings** - Open sidebar → Data Quality → Age Validation
4. **See the report** - Look for the "Data Quality Report" card on main page
5. **Export flagged data** - Try the "Download flagged CSV" button

---

## Need Help?

If something isn't working:
1. Make sure you're in the right folder (`pwd` command shows current folder)
2. Make sure virtual environment is active (you see `(.venv)` in terminal)
3. Copy any error messages - they're helpful for debugging!

Good luck with your demo! 🚀
