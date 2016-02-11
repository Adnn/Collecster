with open("data_manager/forms_admins.py") as f:
        code = compile(f.read(), "data_manager/forms_admins.py", 'exec')
        exec(code)
