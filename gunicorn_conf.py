import os

def load_env(filename):
    # Taken from https://github.com/theskumar/python-dotenv/blob/master/dotenv/main.py#L77
    # (as it is important to strip the potential quotes around values)
    def parse_dotenv(dotenv_path):
        with open(dotenv_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, v = line.split('=', 1)
                v = v.strip("'").strip('"')
                yield k, v

    return ["{}={}".format(k, v) for k, v in parse_dotenv(filename)]

if os.path.isfile(".env"):
    raw_env = load_env(".env")

proc_name = "collecster"
workers   = 3
bind      = ["localhost:9090"]
loglevel  = "debug"
