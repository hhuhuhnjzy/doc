.. _maclient_python_sdk:

maclient_python_sdk: Maze Python Client SDK
==========================================

``maclient_python_sdk`` is the **official Python client library** for the Maze framework, designed to interact with the ``maserver_api`` service. It abstracts away low-level details such as HTTP communication, serialization, and file packaging, enabling users to work in a **clean, declarative** manner to:

- Construct directed acyclic graph (DAG) workflows
- Submit workflows to a remote server
- Query task status and results in real time
- Download execution artifacts
- Manage custom tools

This SDK is **semantically aligned** with the server-side DAG definition (e.g., the ``DAG`` class in ``_graph_builder.py``), but runs on the user's local machine and does **not depend on Ray**.

Installation
------------

.. code-block:: bash

    pip install maclient

Quick Start
-----------

The following is a complete example: building a two-stage workflow ("image captioning → text summarization") and submitting it for execution.

.. code-block:: python

    from maclient import MazeClient, task

    # 1. Connect to the server
    client = MazeClient(server_url="http://localhost:8000")

    # 2. Define task functions (must be decorated with @task)
    @task
    def image_caption(image_path: str) -> dict:
        """Generate image description"""
        # Actual logic is executed on the server
        pass

    @task
    def summarize(text: str) -> dict:
        """Summarize the input text"""
        pass

    # 3. Build the workflow
    dag = client.new_dag(name="image_analysis")

    # Add first task (no dependencies)
    task1_id = dag.add_task(
        func=image_caption,
        inputs={"image_path": "/input/cat.jpg"}  # Static input
    )

    # Add second task (depends on output of task1)
    task2_id = dag.add_task(
        func=summarize,
        inputs={"text": f"{task1_id}.output.caption"}  # Dynamic dependency
    )

    # 4. Submit and wait for result
    run_id = client.submit_dag(dag)
    print(f"Workflow submitted with run_id: {run_id}")

    # 5. Poll until completion
    while not client.is_run_finished(run_id):
        time.sleep(2)

    # 6. Retrieve final result
    result = client.get_task_result(run_id, task2_id)
    print("Summary:", result["data"]["summary"])

Core Concepts
-------------

Task
~~~~

- A task is the fundamental execution unit in a workflow.
- Must be defined with the ``@task`` decorator, which injects metadata (name, input/output schema, resource requirements, etc.).
- The task function **defines only the interface**; actual execution occurs on a server-side Worker.
- Input sources can be:
  1. **Static values**: e.g., ``inputs={"param": "hello"}``
  2. **Output from upstream tasks**: e.g., ``inputs={"param": "task_abc.output.key"}``
  3. **Automatically injected**: e.g., model paths, API keys (determined by server configuration)

Workflow (DAG)
~~~~~~~~~~~~~~

- A directed acyclic graph composed of tasks and their dependencies.
- The ``DAG`` object in the SDK is responsible for building the graph structure but **does not execute it**.
- Upon submission, the entire DAG (including function bytecode) is serialized and sent to the server.

Run
~~~

- Each DAG submission generates a unique ``run_id``.
- A Run includes: the DAG instance, a sandbox directory, task status records, and output files.
- A Run is the basic unit for lifecycle management (can be queried, downloaded, or destroyed).

API Reference
-------------

MazeClient
~~~~~~~~~~

.. autoclass:: maclient.MazeClient
    :members:
    :undoc-members:

    .. automethod:: __init__(self, server_url: str)

        Initialize the client.

        :param server_url: Base URL of the server, e.g., ``"http://localhost:8000"``

    .. automethod:: new_dag(self, name: str = "") -> DAG

        Create a new empty workflow object.

        :param name: Name of the workflow (optional)
        :return: A ``DAG`` instance

    .. automethod:: submit_dag(self, dag: DAG, project_files: Optional[List[str]] = None) -> str

        Submit the DAG to the server for execution.

        :param dag: The constructed ``DAG`` object
        :param project_files: List of local file paths to upload (e.g., custom modules)
        :return: The generated ``run_id``

    .. automethod:: get_task_result(self, run_id: str, task_id: str) -> dict

        Retrieve the execution result of a specified task.

        Returns a dictionary containing:
        - ``status``: ``"success"``
        - ``task_status``: ``"pending" | "running" | "finished" | "failed" | "CANCELLED"``
        - ``data``: (only if finished) the return value of the task
        - ``error``: (only if failed) error message

    .. automethod:: is_run_finished(self, run_id: str) -> bool

        Check if the specified run has finished (all tasks in terminal state).

    .. automethod:: download_run(self, run_id: str, output_dir: str)

        Download the entire run directory to the local machine.

        :param run_id: The run ID
        :param output_dir: Local destination path

    .. automethod:: destroy_run(self, run_id: str)

        Request the server to clean up all artifacts of this run (only if the run has finished).

    .. automethod:: list_tools(self) -> List[dict]

        Retrieve a list of metadata for all registered tools on the server.

    .. automethod:: upload_tool(self, name: str, archive_path: str, **metadata)

        Upload a new tool to the server.

        :param name: Name of the tool
        :param archive_path: Path to the tool package in ZIP format
        :param metadata: Tool metadata (description, type, version, author, usage_notes)

DAG
~~~

.. autoclass:: maclient.DAG
    :members:
    :undoc-members:

    .. automethod:: add_task(self, func: Callable, task_name: Optional[str] = None, inputs: Optional[Dict] = None, resources: Optional[Dict] = None) -> str

        Add a task node to the workflow.

        :param func: A function decorated with ``@task``
        :param task_name: Task alias (optional)
        :param inputs: Dictionary mapping input parameters
        :param resources: Resource requirements (e.g., number of GPUs)
        :return: The generated unique ``task_id``

    .. automethod:: visualize(self)

        Visualize the current workflow structure locally (requires matplotlib).

    .. automethod:: show_structure(self)

        Print the workflow structure as text in the terminal.

@task Decorator
~~~~~~~~~~~~~~~

.. autofunction:: maclient.task

    Decorates a function to make it recognizable by the Maze framework.

    Supports specifying metadata via parameters:

    .. code-block:: python

        @task(
            name="my_image_processor",
            description="Processes input image and returns features",
            resources={"gpu": 1},
            version="1.0"
        )
        def process_image(image_path: str) -> dict:
            pass

    The decorator automatically parses the function signature to generate input/output schemas and injects them into the function's ``_task_meta`` attribute.

Error Handling
--------------

The SDK raises standard exceptions when server errors occur:

- ``maclient.exceptions.MazeAPIError``: Generic API error (e.g., 500)
- ``maclient.exceptions.MazeNotFoundError``: Resource not found (404)
- ``maclient.exceptions.MazeConflictError``: Resource conflict (409)

It is recommended to use try-except blocks for critical operations:

.. code-block:: python

    from maclient.exceptions import MazeNotFoundError

    try:
        client.get_task_result("invalid_run", "t1")
    except MazeNotFoundError as e:
        print("Run or task not found:", e)

Design Principles
-----------------

1. **Local Construction, Remote Execution**: Users build DAGs locally, but all computation occurs on the server.
2. **Function as Task**: Task logic is defined as Python functions, making it clear and intuitive.
3. **Explicit Dependency Declaration**: Data dependencies are expressed via string references (e.g., ``"task_id.output.key"``).
4. **Strong Server Consistency**: The SDK's DAG model is fully compatible with the server-side ``ExecuteDAG``.
5. **Zero Ray Dependency**: The client does not require Ray to be installed or connected.

See Also
--------

- :ref:`maserver_api`: Detailed specification of the server API
- :ref:`maworker`: How Workers execute these tasks
- Full schema definition of the ``@task`` decorator (located in ``maze.core.register``)