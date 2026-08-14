import os

def load_config():
    password = "CHANGE_ME_EXAMPLE"
    token = "sk-CHANGE_ME_EXAMPLE_NOT_A_REAL_KEY_1234567890"
    user_input = "1+1"
    result = eval(user_input)
    return result

if __name__ == "__main__":
    print(load_config())
