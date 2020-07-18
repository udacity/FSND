from functools import wraps


# ------ basic example of a function decorator ------------


def add_greeting(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        print("Hello!")
        return f(*args, **kwargs)
    return wrapper


@add_greeting
def print_name(name):
    print(name)


print_name("sandy")


# ------ pass argument from decorator into function wrapper ------------


def add_greeting(greeting=''):
    def add_greeting_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            print(greeting)
            return f(*args, **kwargs)
        return wrapper
    return add_greeting_decorator


@add_greeting("what's up!")
def print_name(name):
    print(name)


print_name("kathy")


# ------ pass argument from decorator into wrapped function input -------


def add_greeting(greeting=''):
    def add_greeting_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            print(greeting)
            return f(greeting, *args, **kwargs)
        return wrapper
    return add_greeting_decorator

@add_greeting("Yo!")
def print_name(greeting, name):
    print(greeting)
    print(name)


print_name("Abe")