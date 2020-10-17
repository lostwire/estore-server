""" Run application if loaded as a module """
import estore.server.app
import aiohttp.web


if __name__ == '__main__':
    app = estore.server.app.create_app()
    aiohttp.web.run_app(app)
