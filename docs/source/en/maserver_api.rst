.. _maserver_api:

maserver_api: Unified Server API for Maze
=========================================

The ``maserver_api`` module serves as the **centralized server entry point** for the Maze framework. Built on FastAPI, it provides a complete set of RESTful API endpoints for:

- Submitting and managing AI workflows (DAGs)
- Querying task status and results
- Synchronizing runtime files
- Managing reusable tools
- Cleaning up execution artifacts

All APIs communicate via JSON, support file upload/download, and are deeply integrated with the Ray cluster, DAGContext, and task scheduler.

Startup and Configuration
-------------------------

The service is started using the following command:

.. code-block:: bash

    python maserver_api.py

On startup, it automatically:
- Connects to a local or remote Ray cluster (``ray.init(address='auto')``)
- Initializes core services (scheduler, status manager, context manager, etc.)
- Scans the ``maze/library/tools/`` directory to auto-register tool functions
- Starts the background scheduling thread (``dag_manager_daps``)

Configuration is loaded from ``config.toml`` in the project root. Key fields include:

- ``[server] host, port``: Service listening address
- ``[paths] project_root``: Project root path (required)
- ``[paths] model_folder``: Model directory path

Core Service Components
-----------------------

The following global components are initialized at startup and shared via the ``core_services`` dictionary:

- ``dag_submission_queue``: Workflow submission queue (``queue.Queue``)
- ``task_completion_queue``: Task completion callback queue
- ``status_mgr``: ``TaskStatusManager``, tracks the status of all tasks
- ``dag_ctx_mgr``: ``DAGContextManager``, manages runtime context (based on Ray Actor)
- ``resource_mgr``: ``ComputeNodeResourceManager``, manages compute resources
- ``scheduler``: ``TaskScheduler``, responsible for task dispatching and execution

API Endpoints Overview
----------------------

.. list-table::
   :header-rows: 1

   * - Path
     - Method
     - Function
   * - ``/submit_workflow/``
     - POST
     - Submit a new workflow (DAG definition + project code)
   * - ``/runs/{run_id}/summary``
     - GET
     - Retrieve summary information for a specific run
   * - ``/runs/destroy``
     - POST
     - Clean up all artifacts from completed runs
   * - ``/runs/{run_id}/download``
     - GET
     - Download a ZIP archive of the entire run directory
   * - ``/get/``
     - POST
     - Retrieve the result or error of a single task
   * - ``/runs/{run_id}/tasks/{task_id}/cancel``
     - POST
     - Request cancellation of a specific task (best-effort cancellation for running tasks)
   * - ``/files/hashes/{run_id}``
     - GET
     - Get SHA256 hash manifest of all files in the run directory
   * - ``/files/download/{run_id}``
     - POST
     - Download a specified list of files (used by Workers to pull dependencies)
   * - ``/files/upload/{run_id}``
     - POST
     - Upload newly generated files (used by Workers to push results)
   * - ``/tools``
     - GET
     - List all registered tools
   * - ``/tools/upload``
     - POST
     - Upload a new tool (with metadata and code package)
   * - ``/tools/{tool_name}``
     - DELETE
     - Delete a specified tool

Detailed API Specifications
---------------------------

Submit Workflow: ``POST /submit_workflow/``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Request Body (multipart/form-data)**:

- ``workflow_payload``: JSON file containing the DAG definition, formatted as:

  .. code-block:: json

    {
      "tasks": {
        "t1": {
          "func_name": "image_caption",
          "serialized_func": "<base64-encoded cloudpickle>",
          "dependencies": [],
          "inputs": {"image_path": "/input/cat.jpg"}
        },
        "t2": {
          "func_name": "summarize",
          "serialized_func": "...",
          "dependencies": ["t1"],
          "inputs": {"text": "t1.output.caption"}
        }
      }
    }

- ``project_archive``: ZIP file containing user project code (will be extracted into the execution sandbox)

**Response**:

.. code-block:: json

    {
      "status": "success",
      "msg": "Workflow submitted successfully.",
      "run_id": "a1b2c3d4-..."
    }

Get Task Result: ``POST /get/``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Request Body (JSON)**:

.. code-block:: json

    { "run_id": "a1b2c3d4-...", "task_id": "t1" }

**Response (Success)**:

.. code-block:: json

    {
      "status": "success",
      "task_status": "finished",
      "data": { "caption": "A cute cat on the sofa." }
    }

**Response (Failure)**:

.. code-block:: json

    {
      "status": "success",
      "task_status": "failed",
      "error": "ValueError: Invalid image format"
    }

File Synchronization APIs
~~~~~~~~~~~~~~~~~~~~~~~~~

- **Get Hash Manifest**: ``GET /files/hashes/{run_id}``

  Returns a list of all files in the run directory with their relative paths and SHA256 hashes, used by Workers to determine which files to pull.

- **Download Files**: ``POST /files/download/{run_id}``

  Request body is JSON: ``{"files": ["a.py", "data/input.jpg"]}``, returns a ZIP stream.

- **Upload Files**: ``POST /files/upload/{run_id}``

  Uploads using ``multipart/form-data``, with field names as relative file paths (e.g., ``output/result.png``).

Tool Management APIs
~~~~~~~~~~~~~~~~~~~~

- **List Tools**: ``GET /tools``

  Returns a list of metadata for all installed tools, including fields such as ``name``, ``description``, ``type``, ``version``, and ``author``.

- **Upload Tool**: ``POST /tools/upload``

  Form fields:
  - ``tool_name`` (required)
  - ``description``, ``tool_type``, ``version``, ``author``, ``usage_notes``
  - ``tool_archive``: ZIP-formatted tool package

  The tool is extracted to ``{project_root}/maze/model_cache/{tool_name}/``, and metadata is written to ``metadata.json``.

- **Delete Tool**: ``DELETE /tools/{tool_name}``

  Safely deletes the specified tool directory (with path validation to prevent directory traversal).

Run Management APIs
~~~~~~~~~~~~~~~~~~~

- **Get Run Summary**: ``GET /runs/{run_id}/summary``

  Returns status, name, execution time, and other information for all tasks in the run.

- **Download Run Artifacts**: ``GET /runs/{run_id}/download``

  Returns a ZIP archive of the entire run directory, useful for archiving or debugging.

- **Destroy Run**: ``POST /runs/destroy``

  Request body: ``{"run_id": "..."}``. Only runs where **all tasks have terminated** can be destroyed; otherwise, a 400 error is returned.

- **Cancel Task**: ``POST /runs/{run_id}/tasks/{task_id}/cancel``

  Sets the task status to ``CANCELLED``. If the task is currently running, attempts a "best-effort" cancellation via Ray.

Error Handling
--------------

- **400 Bad Request**: Invalid request parameters (e.g., attempting to destroy an active run)
- **404 Not Found**: ``run_id`` or ``task_id`` does not exist
- **409 Conflict**: Resource conflict (e.g., uploading a tool with a duplicate name)
- **500 Internal Server Error**: Internal service exception (includes full traceback in logs)

Logging and Observability
-------------------------

- Uses ``maze.utils.log_config.setup_logging(mode='server')`` to initialize structured logging
- Key operations (submission, cancellation, upload, destruction) are logged at INFO level
- Exception paths include full stack traces (``exc_info=True``)
- Logs are output to both console and file (depending on configuration)

See Also
--------

- :ref:`maworker`: How Workers use these APIs for file synchronization
- :ref:`mapath`: Scheduling logic of ``TaskScheduler`` and ``dag_manager_daps``
- :ref:`maregister`: How tools are registered via ``task_registry``
- ``DAGContextManager``: Underlying mechanism for task result storage and retrieval