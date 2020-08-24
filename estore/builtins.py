import sys

async def length(obj):
    return await getattr(obj, '__length__')()

def register():
    sys.modules['builtins'].length = length
