import estore.server.db.sqlite.engine

async def initialize(config, loop):
    backend = config.get('general', 'DB_BACKEND')
    if backend.lower() == 'sqlite':
        return await estore.server.db.sqlite.engine.init(config, loop)
