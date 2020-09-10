import functools

import aiohttp.web

class Application(aiohttp.web.Application):
    def __init__(self, name, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)
        self.__name = name
        self.__children={}

    def get_name(self):
        return self.__name

    def add_get(self, path, callback, **options):
        if not 'name' in options:
            options['name'] = callback.__name__
        self.add_routes([aiohttp.web.get(path, callback, **options)])

    def add_post(self, path, callback, **options):
        if not 'name' in options:
            options['name'] = callback.__name__
        self.add_routes([aiohttp.web.post(path, callback, **options)])

    def add_view(self, path, callback, **options):
        if not 'name' in options:
            options['name'] = callback.__name__
        self.add_routes([aiohttp.web.view(path, callback, **options)])

    def add_subapp(self, path, app):
        super(Application, self).add_subapp(path, app)
        name = app.get_name()
        if name:
            self.__children[name] = app

    def url_for(self, name, *args, **kwargs):
        if '.' in name:
            child_name, rest = name.split('.', 1)
            return self.__children[child_name].url_for(rest, *args, **kwargs)
        return str(self.router[name].url_for(*args, **kwargs))

class Response:
    def __init__(self, env):
        self.__env = env
    def redirect(self):
        pass
    async def render_template(self, name, **kwargs):
        template = self.__env.get_template(name)
        return aiohttp.web.Response(
            text=await template.render_async(**kwargs), content_type='text/html')

def unpack_match_info(f):
    @functools.wraps(f)
    def wrapper(obj, request):
        return f(obj, request, **request.match_info)
    return wrapper
