import inspect
import pathlib
from functools import wraps

DEBUG = True

NUMBER = (int, float)
PATH = (str, pathlib.Path)
ANY = object
JSON = (dict, list)


"""Main class"""
class ArgumentVerifier:
    def __init__(self, InstanceType, ArgumentNumber: int, AllowEmpty : bool = False):
        self.InstanceType = InstanceType
        self.ArgumentNumber = ArgumentNumber
        self.AllowEmpty = AllowEmpty   # True : un appel sans aucun argument est accepté

        if isinstance(InstanceType, list) and len(InstanceType) != ArgumentNumber:
            raise ValueError(
                f"ArgumentVerifier : {len(InstanceType)} types donnés pour {ArgumentNumber} arguments"
            )

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
    def _resolve_type(self, Expected):
        if isinstance(Expected, type):
            return Expected
        if isinstance(Expected, tuple):
            return Expected
        if callable(Expected):
            return Expected()
        return Expected

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
        if len(args) == 0 and self.AllowEmpty:
            return True
        if len(args) != self.ArgumentNumber:
            return False
        if isinstance(self.InstanceType, list):
            for Target, Expected in zip(args, self.InstanceType):
                Expected = self._resolve_type(Expected)
                if Expected is object:
                    continue
                if not isinstance(Target, Expected):
                    return False
        else:
            Expected = self._resolve_type(self.InstanceType)
            for Target in args:
                if Expected is object:
                    continue
                if not isinstance(Target, Expected):
                    return False

        return True

"""Decorator :
    Les arguments sont liés à la signature de la fonction (valeurs par défaut et kwargs inclus)
    avant d'être vérifiés. Le premier argument (self / cls) est ignoré.
    Si DEBUG est False, la fonction n'est pas wrappée (aucun coût à l'exécution).
"""
def Verify(Verifier):
    def Decorator(Func):
        if not DEBUG:
            return Func
        # Signature résolue au premier appel : à la décoration, les annotations
        # peuvent encore référencer la classe en cours de définition (ex: Other: Udim)
        Cache = {}

        @wraps(Func)
        def Wrapper(*args, **kwargs):
            if "Signature" not in Cache:
                Cache["Signature"] = inspect.signature(Func)
            Bound = Cache["Signature"].bind(*args, **kwargs)
            Bound.apply_defaults()
            Values = list(Bound.arguments.values())[1:]
            if not Verifier.Verifier(*Values):
                raise TypeError(
                    f"Arguments invalides pour {Func.__name__}"
                )
            return Func(*args, **kwargs)
        return Wrapper
    return Decorator