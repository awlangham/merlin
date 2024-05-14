import click
from functools import wraps

def pass_node_name(func):
    @wraps(func)
    @click.pass_context
    def new_func(context, *args, **kwargs):
        return func(context.obj['NODE'], *args, **kwargs)
    return new_func