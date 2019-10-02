import estore.view.auth

async def attach(app, db, pika):
    auth = estore.view.auth.View(injector)
    app.router.add_post('/login', auth.login)
    app.router.add_post('/logout', auth.logout)
    app.router.add_post('/register', auth.register)
    """
    app.router.add_get('/', functools.partial(req_wrapper, functools.partial(views.index, app.loop)))
    app.router.add_post('/testing', functools.partial(req_wrapper, handler.testing))
    app.router.add_post('/subscribe/{entity}', functools.partial(req_wrapper, handler.subscribe))
    app.router.add_post('/{stream}/{name}', functools.partial(req_wrapper, handler.add_event))
    app.router.add_get('/ws', functools.partial(req_wrapper, handler.notify))
    app.router.add_get('/{stream}', functools.partial(req_wrapper, handler.get_events))
    """
