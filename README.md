# Overview

Plaid Aggregator provides a simple way to download your latest bank transactions. By running the app, you'll have the option to link your bank account(s) and fetch your transactions. When you click fetch, your latest transactions will be displayed in the browser, and they will also be saved to a CSV called `transactions_[timestamp].csv`

# Setup

Head over to Plaid's [site](https://dashboard.plaid.com/overview), make a free account, and request Developer access. You will have to fill out a form, which they will look over, and within a day or two you should get an email confirming that you have developer access.

Once you have access to Developer mode (not just Sandbox mode), head over to the [keys](https://dashboard.plaid.com/developers/keys) page and copy your client ID, Sandbox secret, and Development secret into the file called `template.env`. Also be sure to change `PLAID_ENVIRONMENT` to `development`. Then rename this file to `.env` using the Terminal command `mv template.env .env`. 

Next, make a new virtual environment by running `python -m venv venv`. Ensure you are running python version `3.11+` byt checking with the command `python --version`. You may need to reinstall python or run `python3.11 --version` to access this version.

Activate the virtual environment by running `source venv/bin/activate` (macOS) or `.\venv\Scripts\activate` (windows). Then use the package manager `pip` to install the necessary 3rd-part libraries by running `pip install -r requirements.txt`. 

# Usage

With the virtual environment set up and activated, run `python app.py`. This will start your Flask server. Copy the URL displayed in the terminal and paste it into your browser. You should see a button that says `Connect with Plaid`. 

Find your bank among the options and enter your credentials. Follow prompts for two-factor authentication if necessary. Once complete, a button should appear that says `Fetch transactions`. Clicking this button will display your recent transactions in the browser and also download them as a CSV.

# Questions / Suggestions?

Please reach out to ariessunfeld@gmail.com! :)
 
