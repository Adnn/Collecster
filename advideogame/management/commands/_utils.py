def print_validationerror(command, e):
    for error in e:
        if isinstance(error, tuple):
            command.stderr.write("{}:\n * {}".format(error[0], "\n * ".join(error[1])))
        else:
            command.stderr.write(error)
