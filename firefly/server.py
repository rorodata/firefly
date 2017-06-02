from gunicorn.app.base import Application

class FireflyServer(Application):
    def __init__(self, wsgiapp, options=None):
        self.options = options or {}
        self.wsgiapp = wsgiapp
        super(FireflyServer, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in self.options.items()
                       if key in self.cfg.settings and value is not None])
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.wsgiapp
