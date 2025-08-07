Agent Framework Integration: AutoGen Mode
=========================================

This section introduces the AutoGen mode in Maze, which uses dynamic workflow-based agent routing.

Overview
--------

AutoGen mode introduces `workflow_type`-based routing. The host manages multiple agent pools, each corresponding to a workflow type. Workers register themselves with specific workflow types they support.

Step 1: Launch the Host Node
----------------------------

.. code-block:: bash

    python run_host.py --host_addr 127.0.0.1:5003 --flask_port 5002 \
        --agent_pools '{"gaia_file": ["agent1", "agent2"], "gaia_speech": ["agent3"]}'

.. list-table:: Argument Descriptions
   :widths: 20 80
   :header-rows: 1

   * - --host_addr
     - gRPC server address the host listens on
   * - --flask_port
     - Port to receive DAG submission requests
   * - --agent_pools
     - JSON string mapping `workflow_type` → agent list

Step 2: Launch Worker Nodes
---------------------------

Each agent in the pool must have a dedicated worker process:

.. code-block:: bash

    # Worker for workflow 'gaia_file'
    python run_worker.py --host 127.0.0.1:5003 --name agent1 --workflow_type gaia_file

    python run_worker.py --host 127.0.0.1:5003 --name agent2 --workflow_type gaia_file

    # Worker for 'gaia_speech'
    python run_worker.py --host 127.0.0.1:5003 --name agent3 --workflow_type gaia_speech

.. list-table:: Worker Argument Descriptions
   :widths: 20 80
   :header-rows: 1

   * - --host
     - Host address of the master gRPC server
   * - --name
     - Unique worker agent name (must match `agent_pools`)
   * - --workflow_type
     - Type of workflow this worker handles

Step 3: Submit a DAG Task
-------------------------

From a client:

.. code-block:: bash

    python dispatch_task.py --master_addr "127.0.0.1:5002"

The `dispatch_task.py` script will:
- Submit a DAG task via Flask
- Automatically tag each task with a `workflow_type` (e.g., `gaia_file`)
- Host routes task to an agent in corresponding agent pool (round-robin)
