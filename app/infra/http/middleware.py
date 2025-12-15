
class ForceScriptName:
    def __init__(self, app, script_name):
        self.app = app
        self.script_name = script_name

    def __call__(self, environ, start_response):
        if self.script_name:
            environ['SCRIPT_NAME'] = self.script_name
            if environ.get('PATH_INFO', '').startswith(self.script_name):
                environ['PATH_INFO'] = environ['PATH_INFO'][len(self.script_name):]
        return self.app(environ, start_response)
