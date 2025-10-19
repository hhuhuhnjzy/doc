.. _maregister:

maregister: MaRegister — Task Registry and Metadata Center for Maze
===================================================================

The ``maregister`` module implements the **Task Registry** of the Maze framework, known as **MaRegister**.
It is responsible not only for centrally registering all schedulable atomic tasks ("tool functions"), but also for managing their **complete metadata**, including functional descriptions, input/output specifications, and resource requirements.
This metadata serves as the foundation for DAG construction, scheduling decisions, execution validation, and observability.

Task Metadata Model
-------------------

Each task declares its full metadata via the ``@task`` decorator. This information is stored in the function object's ``_task_meta`` attribute with the following structure:

.. code-block:: python

    func._task_meta = {
        'name': str,                      # Unique task identifier (required)
        'description': str,               # Functional description
        'input_parameters': dict,         # Input parameters schema (in JSON Schema format)
        'output_parameters': dict,        # Output parameters schema
        'resources': {
            'type': str,                  # Task type: 'cpu' | 'gpu' | 'io'
            'cpu_num': int,               # Number of required CPU cores
            'mem': int,                   # Required memory (MB)
            'gpu_mem': int,               # Required GPU memory (MB)
            'model_name': Optional[str],  # Dependent model name (e.g., "llama-3-8b")
            'backend': Optional[str]      # Execution backend (e.g., "vllm", "huggingface")
        }
    }

**Special Type Support**: Predefined type constants can be used in ``input_parameters``:

- ``TYPE_FILEPATH = "filepath"``
- ``TYPE_FOLDERPATH = "folderpath"``

These denote file or directory path parameters, enabling downstream I/O optimization or sandbox security checks.

Task Registration Mechanism
---------------------------

1. **Manual Registration (Development/Testing)**
   Explicitly register a decorated function using ``task_registry.register_task(func)``:

   .. code-block:: python

       @task(
           name="image_caption",
           description="Generate descriptive text for an input image",
           input_parameters={"image": {"type": "filepath"}},
           output_parameters={"caption": {"type": "string"}},
           task_type="gpu",
           gpu_mem=4096,
           model_name="llava-v1.6"
       )
       def image_caption(image: str) -> dict:
           ...

       task_registry.register_task(image_caption)

2. **Automatic Discovery (Production Deployment)**
   Call ``discover_tasks(tasks_root_path, package_root_path)`` to scan a specified directory:

   - Recursively traverse all ``.py`` files under ``tasks_root_path`` (excluding ``__init__.py``, etc.)
   - Dynamically import each module and check if functions contain the ``_task_meta`` attribute
   - Automatically register all valid tasks

   This mechanism allows new tools to be integrated simply by:
   - Placing the function in the ``tools/`` directory
   - Adding the ``@task(...)`` decorator
   The Maze system will automatically recognize it—**no changes to registration code are required**.

Task Invocation and Validation
------------------------------

Registered tasks can be retrieved and executed by name:

.. code-block:: python

    func = task_registry.get_task("image_caption")
    result = func(image="/data/img.jpg")

MaRegister **does not handle parameter validation or resource allocation** (these are managed by the scheduler and executor), but provides full metadata for downstream components:

- **DAG Builder**: Validates node arguments against the ``input_parameters`` schema
- **MaPath Scheduler**: Uses ``resources`` (e.g., ``gpu_mem``) to select appropriate execution nodes
- **malearn Predictor**: Maps ``name`` to tool types (e.g., ``"vlm_process"``) for feature extraction

Integration with the Maze Framework
-----------------------------------

+------------------+-------------------------------------------------------------------------------------+
| Module           | How It Uses MaRegister                                                              |
+==================+=====================================================================================+
| **DAG Parser**   | Looks up the ``func`` field in JSON nodes to retrieve the function object and input |
|                  | schema, then validates argument correctness                                       |
+------------------+-------------------------------------------------------------------------------------+
| **MaPath**       | Uses ``resources`` fields (e.g., ``type``, ``gpu_mem``) for resource-aware          |
| **Scheduler**    | scheduling and node placement                                                       |
+------------------+-------------------------------------------------------------------------------------+
| **malearn**      | Maps task ``name`` to prediction model types (e.g., ``"llm_process"``), avoiding    |
|                  | duplication of feature logic                                                        |
+------------------+-------------------------------------------------------------------------------------+
| **Monitoring**   | Uses ``description`` and ``model_name`` to generate human-readable task trace logs  |
| **System**       |                                                                                     |
+------------------+-------------------------------------------------------------------------------------+

Typical Workflow Example
------------------------

1. User defines a tool function with decorator:

   .. code-block:: python

       @task(name="speech_to_text", task_type="gpu", gpu_mem=2048)
       def stt(audio_path: str) -> dict:
           ...

2. System automatically registers on startup:

   .. code-block:: python

       task_registry.discover_tasks("src/tools", "src")
       # Log: Successfully registered task: speech_to_text

3. User submits a DAG:

   .. code-block:: json

       {"nodes": [{"id": "t1", "func": "speech_to_text", "args": {"audio_path": "a.wav"}}]}

4. DAG builder queries registry → Scheduler checks resource needs → Executor loads model → Task completes

Design Advantages
-----------------

- **Declarative**: Task capabilities and requirements are explicitly declared, improving system understandability
- **Strong Typing**: Input/output schemas enable static/dynamic validation, reducing runtime errors
- **Resource-Aware**: Scheduler makes precise placement decisions based on exact resource demands
- **Non-Intrusive**: Business logic is fully decoupled from framework metadata
- **Extensible**: New tasks can be added without modifying core scheduling logic

Exceptions and Logging
----------------------

- **Duplicate Registration**: Tasks with the same name will overwrite the previous one, with a WARNING log (enables hot-reloading during development)
- **Invalid Tasks**: Functions without the ``@task`` decorator or missing ``name`` are skipped, with an ERROR log
- **Import Failure**: Errors in a single module do not affect registration of other tasks (fail-safe design)

Related Constants
-----------------

- ``TYPE_FILEPATH = "filepath"``
- ``TYPE_FOLDERPATH = "folderpath"``

These types can be used for future I/O optimization, sandbox path mapping, or distributed file system mounting.

See Also
--------

- :ref:`mapath`: How the scheduler uses ``resources`` for node selection
- :ref:`malearn`: How task ``name`` is mapped to prediction models