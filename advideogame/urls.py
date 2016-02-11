with open("data_manager/urls.py") as f:
        code = compile(f.read(), "data_manager/urls.py", 'exec')
        exec(code)

