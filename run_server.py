import os
import argparse
import cherrypy
import json
import lmdb

from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))

# settings
STATE_DATA_DIR = 'data'
TASKS_JSON = os.path.join(STATE_DATA_DIR, 'tasks.json')

# custom filters
def commas(value):
    return "{:,.0f}".format(value)
env.filters[commas.__name__] = commas

class Server(object):
    @cherrypy.expose
    def index(self):
        if not os.path.exists(STATE_DATA_DIR):
            os.makedirs(STATE_DATA_DIR)
        if not os.path.exists(TASKS_JSON):
            with open(TASKS_JSON, 'w') as f:
                f.write('{}')
        with open(TASKS_JSON, 'r') as f:
            tasks_data = json.load(f)

        tmpl = env.get_template('index.html')
        return tmpl.render(tasks_data=tasks_data)

    @cherrypy.expose
    def task(self, task_id=None):
        if task_id is None:
            raise cherrypy.HTTPRedirect("/")

        # checks
        if not os.path.exists(TASKS_JSON):
            return "Invalid state: {0} does not exist!".format(TASKS_JSON)
        with open(TASKS_JSON, 'r') as f:
            tasks_data = json.load(f)

        if task_id not in tasks_data:
            return "Invalid state: cannot find task_id {0}!".format(task_id)

        # get image from remaining list file
        remaining_list_file = os.path.join('data', task_id, 'remaining_list.txt')
        with open(remaining_list_file, 'r') as f:
            image_name = next(f)
            image_name = image_name.strip()

        # variables to pass into template
        task = tasks_data[task_id]
        progress_percent = 100.*task['num_completed'] / task['num_total_images']
        num_hot_keys = min(10, len(task['classes']))

        tmpl = env.get_template('task.html')
        return tmpl.render(task=task, progress_percent=progress_percent, num_hot_keys=num_hot_keys, image_name=image_name)

    @cherrypy.expose
    def write(self, task_id=None, image_id=None, label=None):
        if task_id is None:
            return "Invalid state: task_id not specified"
        if image_id is None:
            return "Invalid state: image_id not specified"
        if label is None:
            return "Invalid state: annotation label not specified"

        # add annotation to database
        db_path = os.path.join('data', task_id, 'annotations')
        with lmdb.open(db_path, map_size=pow(2, 40)) as env:
            with env.begin(write=True) as txn:
                result = txn.put(str(image_id), str(label))

        # remove entry from remaining file
        remaining_file = os.path.join('data', task_id, 'remaining_list.txt')
        os.system('tail -n +2 {0} > tmp.txt'.format(remaining_file))
        os.system('rm {0}'.format(remaining_file))
        os.system('mv tmp.txt {0}'.format(remaining_file))

        # update json file
        with open(TASKS_JSON, 'r') as f:
            data = json.load(f)
        data[task_id]['num_completed'] += 1
        with open(TASKS_JSON, 'w') as f:
            json.dump(data, f, sort_keys=True, indent=4, separators=(',', ': '))

        raise cherrypy.HTTPRedirect("/task/{0}".format(task_id))

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
