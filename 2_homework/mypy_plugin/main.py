from mypy.plugin import Plugin
from mypy.types import AnyType, NoneType, TypeOfAny
from mypy.nodes import ClassDef, Argument, Var, ARG_STAR
from mypy.plugins.common import add_method, add_method_to_class


def analyze(ctx):
    nameless_var = Var("")
    args = []
    for attr_name, attr_node in ctx.cls.info.mro[0].names.items():
        args.append(
            Argument(nameless_var, attr_node.type, None, ARG_STAR),
        )
    add_method_to_class(
        ctx.api,
        ctx.cls,
        '__init__',
        args=args,
        return_type=NoneType(),
    )
    return True


class CustomPlugin(Plugin):

    def get_class_decorator_hook_2(self, fullname: str):
        if fullname == 'dataklasses.dataklass':
            return analyze


def plugin(version: str):
    return CustomPlugin
