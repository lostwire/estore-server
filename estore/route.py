import estore.view.auth
import estore.view.consumer

def attach(app, model):
    auth = estore.view.auth.View(model)
    consumer = estore.view.consumer.init(model)
    app.router.add_get('/ws', consumer.websocket)
    app.router.add_post('/login', auth.login)
    app.router.add_post('/logout', auth.logout)
    app.router.add_post('/register', auth.register)
    app.router.add_post('/subscribe', consumer.subscribe)
    app.router.add_post('/test', auth.test)
    app.router.add_get('/{stream}', auth.test)
    app.router.add_post('/{stream}/{name}', consumer.add_event)
    app.router.add_get('/get_stream/{stream}', consumer.get_stream)
