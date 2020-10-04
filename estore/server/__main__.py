import logging
import sys

import estore.server.app


if __name__ == '__main__':
    app = estore.server.app.init()
    app.run()
