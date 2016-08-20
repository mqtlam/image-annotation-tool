# class-annotation-tool
Annotation tool for images with class labels

## Instructions

Launch server:

```bash
python run_server.py --port 8080 --host 0.0.0.0
```

Navigate to `localhost:8080`. The home page contains a list of annotation tasks. Clicking on a task goes to a page for annotating images.

Create a task with the following command:

```bash
python create_task.py unique_task_id "Readable Title for Task" /path/to/images/folder class0 class1 class2 ...
```

Usually class0, class1, class2, etc. are "Correct", "Plausible" and "Incorrect". The system is flexible to add as many classes as needed.

Once the command is finished running, the task will appear on the home page.

After a task is finished, evaluation can be run with the following script:

```bash
python evaluate_task.py unique_task_id
```

The default arguments assume the classes are "Correct", "Plausible" and "Incorrect". The script will print out the counts for these classes as well as the total.
