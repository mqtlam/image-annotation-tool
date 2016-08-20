#!/usr/bin/env python
"""
Create an annotation task from a set of images.
"""

import os
import argparse
import json
import shutil
from glob import glob

STATE_DATA_DIR = 'data'
TASKS_JSON = os.path.join(STATE_DATA_DIR, 'tasks.json')

def create_task_directory(args):
    """Helper to create task directory.

    Postconditions:
        creates a directory

    Args:
        args: command line args
    """
    task_dir = os.path.join('data', args.id)
    if not os.path.exists(task_dir):
        os.makedirs(task_dir)

def create_symlinks(args):
    """Helper to create symbolic links.

    Preconditions:
        symbolic links don't already exist

    Postconditions:
        creates symbolic links

    Args:
        args: command line args
    """
    public_images_dir = os.path.join('public', 'images')
    if not os.path.exists(public_images_dir):
        os.makedirs(public_images_dir)

    data_symlink_file = os.path.join('data', args.id, 'images')
    os.symlink(args.images_dir, data_symlink_file)

    public_symlink_file = os.path.join('', public_images_dir, args.id)
    os.symlink(os.path.join('../../', data_symlink_file), public_symlink_file)

def create_images_list(args):
    """Helper to create image list file.

    Postconditions:
        creates a text file

    Args:
        args: command line args

    Returns:
        number of images
    """
    task_dir = os.path.join('data', args.id)
    data_symlink_file = os.path.join(task_dir, 'images')
    images_list_file = os.path.join(task_dir, 'images_list.txt')
    remaining_list_file = os.path.join(task_dir, 'remaining_list.txt')

    # create images list
    os.system("ls {0} > {1}".format(data_symlink_file, images_list_file))
    shutil.copyfile(images_list_file, remaining_list_file)

    # count number of files
    with open(images_list_file, 'r') as f:
        num_images = sum(1 for line in f)
    return num_images

def check_id_exists(args):
    """Helper to check if id already exists in json meta file.

    Args:
        args: command line args

    Returns:
        True if id already exists
    """
    if os.path.exists(TASKS_JSON):
        with open(TASKS_JSON, 'r') as f:
            data = json.load(f)
        return args.id in data
        
    else:
        return False

def update_tasks_json(args, num_images):
    """Helper to update tasks json meta file.

    Postconditions:
        updates json file

    Args:
        args: command line args
        num_images: number of images
    """
    # add new entry to tasks.json
    data = {}
    if os.path.exists(TASKS_JSON):
        with open(TASKS_JSON, 'r') as f:
            data = json.load(f)

    # add new entry to tasks.json
    entry = {}
    entry['id'] = args.id
    entry['title'] = args.title
    entry['num_completed'] = 0
    entry['num_total_images'] = num_images
    entry['classes'] = args.classes
    entry['help_text'] = args.help_text
    data[args.id] = entry

    # save to tasks.json
    with open(TASKS_JSON, 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4, separators=(',', ': '))

def main():
    parser = argparse.ArgumentParser(description='Create task')
    parser.add_argument('id', type=str, help='unique identifier')
    parser.add_argument('title', type=str, help='short title for task')
    parser.add_argument('images_dir', type=str, help='directory to images')
    parser.add_argument('classes', type=str, nargs='+', help='list of class names')
    parser.add_argument('--help_text', type=str, default='No help provided.', help='specify help text for annotaters')
    args = parser.parse_args()

    if check_id_exists(args):
        raise ValueError('id is already taken: {0}'.format(args.id))

    print "Setting up directory..."
    create_task_directory(args)
    print "Setting up symlinks..."
    create_symlinks(args)
    print "Setting up images list..."
    num_images = create_images_list(args)
    print "Setting up json meta file..."
    update_tasks_json(args, num_images)

main()
