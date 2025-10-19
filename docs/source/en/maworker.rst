.. _maworker:

maworker: Maze Distributed Task Execution Unit (Worker)
=======================================================

``maworker`` is not a standalone module file, but refers to the **task execution unit (Worker)** in the Maze framework that runs on each node of a Ray cluster. Its core logic is implemented by the ``remote_task_runner`` function (typically located in ``maze.utils.executor``), responsible for securely and reliably executing individual tasks dispatched by the scheduler, including input resolution, result return, and file synchronization.

Design Goals
------------

- **Strong Isolation**: Each task runs in an isolated ``taskspace`` directory to prevent file pollution.
- **Self-Contained Dependencies**: Ensures execution environment consistency by synchronizing code and data from the Master node.
- **Context Awareness**: Correctly resolves input parameters from upstream tasks or global configuration.
- **Standardized Output**: Uniformly wraps user function return values for consistent DAG state management.
- **Fault Tolerance and Observability**: Captures exceptions, logs execution details, and supports cascading failure handling.

Execution Lifecycle
-------------------

Each worker task undergoes four distinct phases:

1. **File Sync Pull**
   - Fetches the official file hash manifest for the current run from the Master node.
   - Compares against the local ``taskspace/`` directory and downloads only missing or modified files.
   - Uses ZIP streaming for efficient transfer, ensuring the execution environment matches the submission state.

2. **Parameter Resolution**
   - Deserializes the user function (via ``cloudpickle``).
   - Sets ``CUDA_VISIBLE_DEVICES`` (if it's a GPU task).
   - Resolves function arguments from three sources (in priority order):
     a. **Explicit Inputs**: ``task_inputs`` specified in the DAG node (e.g., ``"input": "t1.output.text"``)
     b. **Context Inheritance**: Retrieved from the ``DAGContext`` Actor by parameter name (e.g., model paths, API keys)
     c. **Function Defaults**: Values from the function signature
   - Supports nested dictionary access (e.g., ``"t1.output.result[0].caption"``)

3. **User Function Execution**
   - Changes the working directory to ``taskspace/``, ensuring all file I/O occurs within this isolated sandbox.
   - Invokes the user function and captures its return value.
   - Regardless of success or failure, restores the original working directory to prevent environment leakage.

4. **Result Processing and File Push**
   - **Result Wrapping**: Wraps the user's return value into a dictionary ``{output_key: value}``, matching the ``output_parameters`` declared in ``@task``.
   - **Context Update**: Stores the result in ``DAGContext`` for downstream tasks to consume.
   - **File Push**: Scans for newly created or modified **non-code files** in ``taskspace/`` (e.g., images, audio, intermediate results) and uploads them to the Master node.

Key Mechanisms Explained
------------------------

Task Isolation: The ``taskspace`` Directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each run on a worker node has a dedicated ``./taskspace/`` directory, serving as the **execution sandbox**:

- The current working directory (cwd) of the user function is temporarily switched here.
- Input files (e.g., images, audio) and output files (e.g., generated images) are stored here.
- Code files (`.py`) and cache (``__pycache__``) are excluded from upload—only data files are synchronized.

This mechanism ensures:
- Multiple DAGs or instances of the same DAG do not interfere with each other.
- Task failures do not pollute the global environment.
- Intermediate artifacts are precisely tracked and can be reclaimed.

Input Resolution: Dynamic Dependency Resolution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The worker can resolve dynamic input references in the form ``"task_id.output.key"``:

- Retrieves the full output dictionary of the upstream task via the ``DAGContext`` Actor.
- Extracts the specific field by the ``key`` path (supports nested dictionaries).
- Supports list indexing (e.g., ``"t2.output.items[0]"``).

Example:
.. code-block:: python

    # Upstream task t1 returns: {"image_path": "/tmp/a.jpg", "objects": ["cat", "dog"]}
    # Current task parameters: image="t1.output.image_path", first_obj="t1.output.objects[0]"

    # After resolution:
    # image = "/tmp/a.jpg"
    # first_obj = "cat"

Output Standardization: Single Output Constraint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To simplify DAG state management, Maze enforces that each task has **exactly one output field**:

- The output field name must be explicitly declared in ``@task(output_parameters=...)``.
- The user function's return value is automatically wrapped as ``{output_key: return_value}``.
- If the user returns ``None``, it is stored as ``None``, indicating no valid output.

Example:
.. code-block:: python

    @task(name="summarize", output_parameters={"summary": {"type": "string"}})
    def summarize(text: str) -> str:
        return llm(f"Summarize: {text}")

    # Actual value stored in DAGContext: {"summary": "The quick brown fox..."}

Fault Tolerance and Logging
---------------------------

- **Exception Handling**: All exceptions are caught and returned as ``{"status": "failed", "err_msg": ...}``.
- **Logging**: Uses the standard ``logging`` module, emitting DEBUG-level logs per phase (Sync/Resolve/Execute/Push).
- **Status Reporting**: Execution results (success/failure) are returned via Ray to the scheduler, triggering downstream tasks or cascading cancellation.

Communication with the Master Node
----------------------------------

Workers interact with the Master node via HTTP:

- **Pull Files**: ``GET /files/hashes/<run_id>`` to fetch hash manifest; ``POST /files/download/<run_id>`` to download files.
- **Push Files**: ``POST /files/upload/<run_id>`` to upload newly generated data files.

This design avoids strong dependencies on Redis or shared filesystems, enhancing deployment flexibility.

Performance and Security Considerations
---------------------------------------

- **GPU Isolation**: Achieved via ``CUDA_VISIBLE_DEVICES``, ensuring tasks cannot see each other's GPU usage when sharing.
- **Memory Safety**: Uses ``cloudpickle`` for deserialization, but only for trusted internal functions (controlled by a registry).
- **I/O Optimization**: Only necessary files are synchronized, and `.py`/`.pyc` files are excluded to reduce network overhead.

See Also
--------

- :ref:`maregister`: How tasks declare output specifications via ``@task``
- :ref:`mapath`: How the scheduler dispatches tasks to workers
- :ref:`malearn`: How execution time prediction informs scheduling
- ``DAGContext``: Central store for data exchange between tasks