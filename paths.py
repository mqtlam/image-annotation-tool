import os

class Paths:
    data_dir = 'data'
    tasks_json = os.path.join(data_dir, 'tasks.json')
    public_images_dir = os.path.join('public', 'images')

    @staticmethod
    def task_dir(task_id):
        return os.path.join(Paths.data_dir, task_id)

    @staticmethod
    def images_list(task_id):
        return os.path.join(Paths.task_dir(task_id), 'images_list.txt')

    @staticmethod
    def remaining_list(task_id):
        return os.path.join(Paths.task_dir(task_id), 'remaining_list.txt')

    @staticmethod
    def images_dir(task_id):
        return os.path.join(Paths.task_dir(task_id), 'images')

    @staticmethod
    def annotations_db(task_id):
        return os.path.join(Paths.task_dir(task_id), 'annotations')

    @staticmethod
    def public_task_images_dir(task_id):
        return os.path.join(Paths.public_images_dir, task_id)
