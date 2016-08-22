#!/usr/bin/env python
"""
Delete an annotation task.
"""

import os
import argparse
import json
import shutil

from paths import Paths

def delete_task_directory(args):
    """Helper to delete task directory.

    Postconditions:
        deletes a directory

    Args:
        args: command line args
    """
    task_dir = Paths.task_dir(args.id)
    if os.path.exists(task_dir):
        shutil.rmtree(task_dir)

def delete_symlinks(args):
    """Helper to delete symbolic links.

    Preconditions:
        symbolic links exist

    Postconditions:
        deletes symbolic links

    Args:
        args: command line args
    """
    data_symlink_file = Paths.images_dir(args.id)
    os.remove(data_symlink_file)

    public_symlink_file = Paths.public_task_images_dir(args.id)
    os.remove(public_symlink_file)

def check_id_exists(args):
    """Helper to check if id already exists in json meta file.

    Args:
        args: command line args

    Returns:
        True if id already exists
    """
    if os.path.exists(Paths.tasks_json):
        with open(Paths.tasks_json, 'r') as f:
            data = json.load(f)
        return args.id in data
        
    else:
        return False

def update_tasks_json(args):
    """Helper to update tasks json meta file.

    Preconditions:
        task id key exists in json file

    Postconditions:
        updates json file

    Args:
        args: command line args
    """
    data = {}
    if os.path.exists(Paths.tasks_json):
        with open(Paths.tasks_json, 'r') as f:
            data = json.load(f)

    # delete entry in tasks.json
    data.pop(args.id, None)

    # save to tasks.json
    with open(Paths.tasks_json, 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4, separators=(',', ': '))

def main():
    parser = argparse.ArgumentParser(description='Delete task')
    parser.add_argument('id', type=str, help='unique identifier for task')
    args = parser.parse_args()

    if not check_id_exists(args):
        raise ValueError('task id does not exist: {0}'.format(args.id))

    print "Deleting symlinks..."
    delete_symlinks(args)
    print "Deleting task directory..."
    delete_task_directory(args)
    print "Removing entry from json meta file..."
    update_tasks_json(args)

main()
