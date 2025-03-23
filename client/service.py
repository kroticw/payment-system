from main import CLIENT_PUBLIC_KEY_PATH, CLIENT_PRIVATE_KEY_PATH

SERVER_PUBLIC_KEY_PATH = "server_public_key.pem"

def get_server_public_key():
    with open(SERVER_PUBLIC_KEY_PATH) as f:
        server_public_key = f.read()
        return server_public_key

def get_client_public_key():
    with open(CLIENT_PUBLIC_KEY_PATH) as f:
        client_public_key = f.read()
        return client_public_key

def get_client_private_key():
    with open(CLIENT_PRIVATE_KEY_PATH) as f:
        client_private_key = f.read()
        return client_private_key

# Генерация затеняющего множителя r
def gen_shading_multiplier_r():
    return 1

# Генерация случайного номера купюры
def gen_banknote_number():
    return 1

def get_request_on_banknote(denomination):
    return