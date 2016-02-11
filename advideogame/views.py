with open("data_manager/views.py") as f:
        code = compile(f.read(), "data_manager/views.py", 'exec')
        exec(code)

# Create your views here.
