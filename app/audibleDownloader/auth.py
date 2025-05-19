import audible
import os

# create the file for the first login
# have each one on a different line
# email
# password
# country code https://audible.readthedocs.io/en/latest/marketplaces/marketplaces.html#country-codes
# "True" if you have an audible account before amazon otherwise "False"
def get_login_data():
    path = os.path.expanduser("~/.config/audible/login.info")
    with open(path) as f:
        lines = (line.strip() for line in f.readlines())
        username: str = lines[0]
        password: str = lines[1]
        country_code: str = lines[2]
        pre_amazon_account: bool = lines[3]
    return [username, password, country_code, pre_amazon_account]

# gets your authentication token or creates it if it doesn't exist
def authenticator():
    path = os.path.expanduser("~/.config/audible/audible.auth")
    if os.path.isfile(path):
        auth = audible.Authenticator.from_file(path)
    else:
        os.makedirs(os.path.expanduser("~/.config/audible"), exist_ok=True)
        login_data = get_login_data()
        auth = audible.Authenticator.from_login(
            login_data[0],
            login_data[1],
            locale=login_data[2],
            with_username=login_data[3]
        )
        # Save credentials to file
        auth.to_file(path)
    return auth