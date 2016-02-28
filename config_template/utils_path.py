with open("data_manager/utils_path.py") as f:
        code = compile(f.read(), "data_manager/utils_path.py", 'exec')
        exec(code)
