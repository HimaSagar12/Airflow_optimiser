import ast

class AirflowDagParser:
    def __init__(self, dag_file_content):
        self.dag_file_content = dag_file_content
        self.tree = ast.parse(self.dag_file_content)

    def parse(self):
        dags = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'DAG':
                dag_id = ''
                for keyword in node.keywords:
                    if keyword.arg == 'dag_id':
                        dag_id = keyword.value.s
                
                tasks = self.get_tasks(node)
                dags.append({'dag_id': dag_id, 'tasks': tasks})
        return dags

    def get_tasks(self, dag_node):
        tasks = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) and hasattr(node.value.func, 'id') and 'Operator' in node.value.func.id:
                task_id = ''
                for keyword in node.value.keywords:
                    if keyword.arg == 'task_id':
                        task_id = keyword.value.s
                
                dependencies = self.get_task_dependencies(node)
                tasks.append({'task_id': task_id, 'dependencies': dependencies})
        return tasks

    def get_task_dependencies(self, task_node):
        dependencies = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitShiftRight):
                if isinstance(node.left, ast.Name) and node.left.id == task_node.targets[0].id:
                    if isinstance(node.right, ast.Name):
                        dependencies.append(node.right.id)
        return dependencies