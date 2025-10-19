MazeClient Web API Reference
============================

MazeClient provides a set of RESTful Web APIs based on FastAPI for remotely managing sessions, workflows, tasks, and execution instances. The API supports the complete lifecycle of operations, including creating client sessions, defining workflows, dynamically registering task functions, submitting executions, and querying results.

All endpoints are prefixed with ``/api``. Some paths include dynamic parameters such as ``{session_id}``, ``{workflow_id}``, etc.

Health Check and Resource Overview
----------------------------------

.. http:get:: /api/health

   Health check endpoint that returns service status and resource statistics.

   :statuscode 200: Service is healthy
   :statuscode 503: Service is unavailable

   **Response Example**:

   .. code-block:: json

      {
        "status": "healthy",
        "timestamp": 1712345678.123,
        "sessions_count": 2,
        "workflows_count": 5,
        "runs_count": 3,
        "builtin_tasks_count": 4,
        "total_registered_tasks": 10
      }

.. http:get:: /api/sessions

   Lists all currently active sessions and their resource overview.

   :statuscode 200: Successfully returns the session list

   **Response Fields**:

   - ``session_id``: Unique identifier of the session
   - ``server_address``: Associated Maze server address
   - ``workflows_count``: Number of workflows created in this session
   - ``runs_count``: Number of current running instances
   - ``tasks_count``: Number of registered task functions

Session Management
------------------

.. http:post:: /api/client/create

   Creates a new MazeClient session.

   :statuscode 201: Session created successfully
   :statuscode 400: Invalid request parameters

   **Request Body (JSON)**:

   .. code-block:: json

      {
        "server_address": "127.0.0.1:6380"
      }

   **Response**:

   Returns the ``session_id``, which is required to identify the session in all subsequent operations.

.. http:delete:: /api/{session_id}/cleanup

   Cleans up all resources associated with the specified session (including workflows, running instances, task functions, etc.).

   :param string session_id: Unique identifier of the session
   :statuscode 200: Cleanup successful
   :statuscode 404: Session not found

Workflow Management
-------------------

.. http:post:: /api/{session_id}/workflows/create

   Creates a workflow within the specified session.

   :param string session_id: Unique identifier of the session
   :statuscode 201: Workflow created successfully

   **Request Body (JSON)**:

   .. code-block:: json

      {
        "name": "my_workflow"
      }

   **Response**:

   Returns the ``workflow_id``, used for subsequent task additions and submissions.

.. http:get:: /api/{session_id}/workflows/{workflow_id}/structure

   Retrieves the structure graph of the workflow (task dependency relationships).

   :param string session_id: Unique identifier of the session
   :param string workflow_id: Workflow ID

.. http:delete:: /api/{session_id}/workflows/{workflow_id}/tasks/{task_id}

   Deletes a specified task from the workflow (force delete, ignoring dependencies).

   :param string session_id: Unique identifier of the session
   :param string workflow_id: Workflow ID
   :param string task_id: Task ID

Task Management
---------------

.. http:post:: /api/{session_id}/workflows/{workflow_id}/tasks/add

   Adds a task to the specified workflow.

   :param string session_id: Unique identifier of the session
   :param string workflow_id: Workflow ID

   **Request Body (JSON)**:

   .. code-block:: json

      {
        "function_name": "my_task_func",
        "task_name": "Step 1",
        "inputs": {"param1": "value1"},
        "file_paths": ["/data/file.txt"],
        "resources": {"cpu": "2", "memory": "4G"}
      }

   **Notes**:

   - ``function_name`` must refer to a previously registered task function (built-in or dynamically registered).
   - ``file_paths`` and ``resources`` are optional fields.

.. http:put:: /api/{session_id}/workflows/{workflow_id}/tasks/{task_id}

   Updates the configuration of an existing task (function, inputs, resources, etc.).

.. http:get:: /api/{session_id}/workflows/{workflow_id}/task/{task_id}/info

   Retrieves detailed information about a specific task.

.. http:get:: /api/{session_id}/tasks/available

   Lists all available task functions in the current session (including metadata such as description, input/output parameters, etc.).

Dynamic Task Registration
-------------------------

.. http:post:: /api/{session_id}/tasks/register

   Dynamically registers a task function by uploading a Python code string.

   :param string session_id: Unique identifier of the session

   **Form Parameters**:

   - ``task_code``: Python code string containing the task function definition
   - ``function_name``: Name of the function to register

   **Requirements**:

   The function must be decorated with ``@task``; otherwise, it will not be recognized as a valid task.

Task Package Upload
-------------------

.. http:post:: /api/{session_id}/tasks/upload

   Uploads a ZIP-formatted task package (containing code, dependencies, configuration, etc.).

   :param string session_id: Unique identifier of the session

   **Form Parameters**:

   - ``task_archive``: ZIP file (File)
   - ``description``: Task description
   - ``task_type``: Task type (e.g., "llm", "data_processing")
   - ``version``: Version number (default "1.0.0")
   - ``author``: Author name (default "unknown")

Workflow Execution and Result Query
-----------------------------------

.. http:post:: /api/{session_id}/workflows/{workflow_id}/submit

   Submits a workflow for execution.

   :param string session_id: Unique identifier of the session
   :param string workflow_id: Workflow ID

   **Request Body (JSON)**:

   .. code-block:: json

      {
        "mode": "server"  // Possible values: "server" or "local"
      }

   **Response**:

   Returns the ``run_id``, used for subsequent querying or control.

.. http:post:: /api/{session_id}/tasks/result

   Retrieves the execution result of a specified task (supports synchronous waiting).

   :param string session_id: Unique identifier of the session

   **Request Body (JSON)**:

   .. code-block:: json

      {
        "run_id": "run-123",
        "task_id": "task-456",
        "wait": true,
        "timeout": 300,
        "poll_interval": 2.0
      }

.. http:post:: /api/{session_id}/tasks/result/async

   Asynchronously retrieves task results (based on asyncio polling).

.. http:post:: /api/{session_id}/tasks/cancel

   Cancels the execution of a specified task.

.. http:get:: /api/{session_id}/runs/{run_id}/summary

   Retrieves a summary of the entire run instance (task statuses, execution times, etc.).

.. http:post:: /api/{session_id}/runs/{run_id}/destroy

   Destroys the run instance and releases associated resources.

Frontend and CORS Support
-------------------------

.. http:get:: /

   Serves the built-in web frontend (located at ``frontend/index.html``), which can be used for visual operations.

**CORS Support**: The API has CORS enabled, allowing cross-origin requests from any origin, facilitating integration with web frontends.

Error Handling
--------------

All endpoints return standard HTTP error codes (e.g., 404, 500) and a JSON-formatted error detail upon failure:

.. code-block:: json

   {
     "detail": "Failed to create client: Connection refused"
   }

Logging
-------

Upon startup, the service automatically loads built-in task functions (from ``task.py`` in the same directory) and logs the loading information.