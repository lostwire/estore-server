import views
import functools

async def req_wrapper(handler, req):
    return await handler(req)

def attach_routes(app, db):
    handler = views.Handler(db)
    app.router.add_get('/', functools.partial(views.index, db))
    app.router.add_post('/{stream}/{name}', functools.partial(req_wrapper, handler.add_event))
    app.router.add_get('/{stream}', functools.partial(req_wrapper, handler.get_events))
