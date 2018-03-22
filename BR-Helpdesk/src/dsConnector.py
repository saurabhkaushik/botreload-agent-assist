import datetime

# [START build_service]
from google.cloud import datastore

class dsConnector(object):

    def __init__(self):
        self.client = datastore.Client()
    # [END build_service]
    
    
    # [START add_entity]
    def add_logs(self, req_type, log_txt):
        key = self.client.key('Logs')
    
        task = datastore.Entity(key, exclude_from_indexes=['log'])
    
        task.update({
            'type': req_type,
            'created': datetime.datetime.utcnow(),
            'log': log_txt,
            'done': False
        })
    
        self.client.put(task)
        return task.key
    # [END add_entity]
    
    
    # [START update_entity]
    def mark_done(self, task_id):
        with self.client.transaction():
            key = self.client.key('Task', task_id)
            task = self.client.get(key)
    
            if not task:
                raise ValueError(
                    'Task {} does not exist.'.format(task_id))
    
            task['done'] = True
    
            self.client.put(task)
    # [END update_entity]
    
    
    # [START retrieve_entities]
    def list_tasks(self):
        query = self.client.query(kind='Task')
        query.order = ['created']
    
        return list(query.fetch())
    # [END retrieve_entities]
    
    
    # [START delete_entity]
    def delete_task(self, task_id):
        key = self.client.key('Task', task_id)
        self.client.delete(key)
    # [END delete_entity]
    
    
    # [START format_results]
    def format_tasks(self, tasks):
        lines = []
        for task in tasks:
            if task['done']:
                status = 'done'
            else:
                status = 'created {}'.format(task['created'])
    
            lines.append('{}: {} ({})'.format(
                task.key.id, task['description'], status))
    
        return '\n'.join(lines)
    # [END format_results]
    
    
    def new_command(self, args):
        """Adds a task with description <description>."""
        task_key = self.add_task(self, self.client, args.description)
        print('Task {} added.'.format(task_key.id))
    
    
    def done_command(self, args):
        """Marks a task as done."""
        self.mark_done(self.client, args.task_id)
        print('Task {} marked done.'.format(args.task_id))
    
    
    def list_command(self, args):
        """Lists all tasks by creation time."""
        print(self.format_tasks(self.list_tasks(self.client)))
    
    
    def delete_command(self, args):
        """Deletes a task."""
        self.delete_task(self.client, args.task_id)
        print('Task {} deleted.'.format(args.task_id))

'''
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser.add_argument('--project-id', help='Your cloud project ID.')

    new_parser = subparsers.add_parser('new', help=new_command.__doc__)
    new_parser.set_defaults(func=new_command)
    new_parser.add_argument('description', help='New task description.')

    done_parser = subparsers.add_parser('done', help=done_command.__doc__)
    done_parser.set_defaults(func=done_command)
    done_parser.add_argument('task_id', help='Task ID.', type=int)

    list_parser = subparsers.add_parser('list', help=list_command.__doc__)
    list_parser.set_defaults(func=list_command)

    delete_parser = subparsers.add_parser(
        'delete', help=delete_command.__doc__)
    delete_parser.set_defaults(func=delete_command)
    delete_parser.add_argument('task_id', help='Task ID.', type=int)

    args = parser.parse_args()

    client = create_client(args.project_id)
    args.func(client, args)
'''