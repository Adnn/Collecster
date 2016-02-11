with open("data_manager/config_utils.py") as f:
        code = compile(f.read(), "data_manager/config_utils.py", 'exec')
        exec(code)
