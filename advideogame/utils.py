with open("data_manager/utils.py") as f:
        code = compile(f.read(), "data_manager/utils.py", 'exec')
        exec(code)
