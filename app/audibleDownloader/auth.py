import audible
import os
import ast

# create the file for the first login
# have each one on a different line
# email
# password
# country code https://audible.readthedocs.io/en/latest/marketplaces/marketplaces.html#country-codes
# "True" if you have an audible account before amazon otherwise "False"
def get_login_data(path: os.path):
    with open(path + "login.ini") as f:
        lines = [line.strip() for line in f.readlines()]
        username: str = lines[0]
        password: str = lines[1]
        country_code: str = lines[2]
        pre_amazon_account: bool = ast.literal_eval(lines[3])
    return [username, password, country_code, pre_amazon_account]

# gets your authentication token or creates it if it doesn't exist

class Authentication:
    def __init__(self, path: os.path):
        self.path = path 
        self.file_path = path + "audible.auth"

    def get_authentication(self):
        if os.path.isfile(self.file_path):
            auth = audible.Authenticator.from_file(self.file_path)
        else:
            os.makedirs(self.path, exist_ok=True)
            login_data = get_login_data()
            auth = audible.Authenticator.from_login(
                login_data[0],
                login_data[1],
                locale=login_data[2],
                with_username=login_data[3]
            )
            # Save credentials to file
            auth.to_file(self.file_path)
        return auth