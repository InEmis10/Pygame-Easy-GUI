import pathlib
from functools import wraps

DEBUG = True

NUMBER = (int, float)
PATH = (str, pathlib.Path)
ANY = object
JSON = (dict, list)


"""Main class"""
class ArgumentVerifier:
    def __init__(self, instanceType, argumentNumber: int):
        self.InstanceType = instanceType
        self.ArgumentNumber = argumentNumber

        if isinstance(instanceType, list) and len(instanceType) != argumentNumber:
            self.InstanceType = []
            self.ArgumentNumber = 0

    """_resolve_type:
        TYPE : Private methode
        DESCRIPTION :
            Resolve type check, single type check, list type check or (*)lambda check
        USAGE : NO USAGE
        OTHER:
            (*) -> lamba is used to send data not initialized by the script where you are building your
            ArgumentVerifier , e.g. a class who need to check __add__ and who need an other instance of itself while python process the
            class definition.
    """
    def _resolve_type(self, expected):
        if isinstance(expected, type):
            return expected
        if isinstance(expected, tuple):
            return expected
        if callable(expected):
            return expected()
        return expected

    """Verifier :
        TYPE : Methode
        DESCRIPTION : 
            Allow the user to control argument type passed to a function
        USAGE : 
            1 - After you create you ArgumentVerifier object
            2 - Call verify 
            3 - Return true if all values valid, false if not
    """
    def Verifier(self, *args) -> bool:
        if len(args) != self.ArgumentNumber:
            return False
        if isinstance(self.InstanceType, list):
            for target, expected in zip(args, self.InstanceType):
                expected = self._resolve_type(expected)
                if expected is object:
                    continue
                if not isinstance(target, expected):
                    return False
        else:
            expected = self._resolve_type(self.InstanceType)
            for target in args:
                if expected is object:
                    continue
                if not isinstance(target, expected):
                    return False

        return True

"""Decorator"""
def Verify(verifier):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not verifier.Verifier(*args[1:]):
                raise TypeError(
                    f"Arguments invalides pour {func.__name__}"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator