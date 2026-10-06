from __future__ import annotations
from typing import overload, Generic, TypeVar
T = TypeVar("T")

"""
Type T -> il décrit le type passer a la property permet d'avoir une property qui possède l'auto completion du type de class qui lui est passé (obj ou cls)

Property sert a définir des variables dans les objets qui puissent trigger un changement donc Property remplace les Propriété des objets necessitants une update
graphique ou un trigger d'event utilisateur ou interne.
"""

class Property(Generic[T]):
    def __init__(self, default : T = None, *, layout : bool = False, draw : bool = True):
        self.Default : T = default
        self.Layout = layout
        self.Draw = draw

    def __set_name__(self, owner : type, name : str):
        self.Name = name
        self.Storage = "_" + name

    @overload
    def __get__(self, obj : None, owner : type) -> Property[T]: ...
    @overload
    def __get__(self, obj : object, owner : type) -> T: ...
    def __get__(self, obj, owner=None):
        if obj is None:
            return self
        return getattr(obj, self.Storage, self.Default)

    def __set__(self, obj : "GuiObject", value):
        from .Application import Application
        if getattr(obj, self.Storage, self.Default) == value:
            return
        setattr(obj, self.Storage, value)
        if not hasattr(obj, "_OnPropertyChanged"):
            return
        obj._OnPropertyChanged(self.Name, self.Layout)
        if self.Draw and Application.Current:
            Application.Current.RequestRedraw()



