import audible
import os
import ast
import json

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
        self.audible_json = path + "audible.json"
        self.config_toml = path + "config.toml"
        # needed for the audible cli package to use the same path
        if "AUDIBLE_CONFIG_DIR" not in os.environ:
            os.putenv("AUDIBLE_CONFIG_DIR", path[:-1])


    def get_authentication(self):
        if os.path.isfile(self.audible_json):
            auth = audible.Authenticator.from_file(self.audible_json)
        else:
            os.makedirs(self.path, exist_ok=True)
            login_data = get_login_data(self.path)
            auth = audible.Authenticator.from_login(
                login_data[0],
                login_data[1],
                locale=login_data[2],
                with_username=login_data[3]
            )
            # Save credentials to file
            auth.to_file(self.audible_json)

        # get the activation bytes and save them
        with open(self.audible_json, "r") as f:
            json_data = json.load(f)

        if json_data["activation_bytes"] is None:
            json_data["activation_bytes"] = auth.get_activation_bytes()
            json.dump(json_data, open(self.audible_json, "w"))

        # for the audible cli package
        if not os.path.isfile(self.config_toml):
            os.makedirs(self.path, exist_ok=True)
            content = ('title = "Audible Config File"\n\n'
            '[APP]\n'
            'primary_profile = "audible"\n\n'
            '[profile.audible]\n'
            'auth_file = "audible.json"\n'
            f'country_code = "{get_login_data(self.path)[2]}"'
            )
            open(self.config_toml, "w").write(content)

        return auth