import os
import argparse
import cherrypy
import json

from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))

# settings
STATE_DATA_DIR = 'state_data'
TASKS_JSON = os.path.join(STATE_DATA_DIR, 'tasks.json')

# custom filters
def commas(value):
    return "{:,.0f}".format(value)
env.filters[commas.__name__] = commas

class Server(object):
    @cherrypy.expose
    def index(self):
        if not os.path.exists(TASKS_JSON):
            return "Invalid state: {0} does not exist!".format(TASKS_JSON)
        with open(TASKS_JSON, 'r') as f:
            tasks_data = json.load(f)

        tmpl = env.get_template('index.html')
        return tmpl.render(tasks_data=tasks_data)

    @cherrypy.expose
    def task(self, task_id=None):
        if task_id is None:
            raise cherrypy.HTTPRedirect("/")

        if not os.path.exists(TASKS_JSON):
            return "Invalid state: {0} does not exist!".format(TASKS_JSON)
        with open(TASKS_JSON, 'r') as f:
            tasks_data = json.load(f)

        if task_id not in tasks_data:
            return "Invalid state: cannot find task_id {0}!".format(task_id)

        # variables to pass into template
        task = tasks_data[task_id]
        progress_percent = 100.*task['num_completed'] / task['num_total_images']
        num_hot_keys = min(10, len(task['classes']))

        tmpl = env.get_template('task.html')
        return tmpl.render(task=task, progress_percent=progress_percent, num_hot_keys=num_hot_keys)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run annotation server.')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='socket host')
    parser.add_argument('--port', type=int, default=8080, help='socket port')
    args = parser.parse_args()

    conf = {
        'global' : {
            'server.socket_host' : args.host,
            'server.socket_port' : args.port
            },
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    cherrypy.quickstart(Server(), '/', conf)
