Agent Framework Integration: AgentScope Mode
============================================

This section introduces how to use Maze with AgentScope for fully distributed RPC-based agent orchestration.

Overview
--------

AgentScope mode is built on a Host–Worker architecture:

- **Host Node**:
  - Runs `run_host.py`
  - Acts as a central controller and Flask API server
  - Uses `agent_pools` to map workflow types to specific agents on specific nodes

- **Worker Node**:
  - Runs `run_worker.py`
  - Registers RPC endpoint and exposes `agent_name`, `workflow_types`

- **Client (Dispatch Task)**:
  - Calls `dispatch_task.py` to submit DAGs to the Host's Flask server

Step 1: Launch the Host Node
----------------------------

.. code-block:: bash

    python run_host.py --port 5002 \
        --agent_pools '{"gaia_file":["file_agent@127.0.0.1:6001"], \
                        "gaia_vision":["vision_agent@127.0.0.1:6002"], \
                        "gaia_speech":["speech_agent@127.0.0.1:6003"], \
                        "gaia_reason":["reason_agent@127.0.0.1:6004"]}'

.. list-table:: Argument Descriptions
   :widths: 20 80
   :header-rows: 1

   * - --port
     - Port for the host's Flask API
   * - --agent_pools
     - JSON dict mapping workflow types to `agent_name@host:port` endpoints

Step 2: Launch Worker Nodes
---------------------------

Each worker must match an entry in the `agent_pools`.

.. code-block:: bash

    python run_worker.py --host 127.0.0.1 --port 6001 \
        --agent_name file_agent --workflow_types gaia_file

    python run_worker.py --host 127.0.0.1 --port 6002 \
        --agent_name vision_agent --workflow_types gaia_vision

    python run_worker.py --host 127.0.0.1 --port 6003 \
        --agent_name speech_agent --workflow_types gaia_speech

    python run_worker.py --host 127.0.0.1 --port 6004 \
        --agent_name reason_agent --workflow_types gaia_reason

.. list-table:: Worker Argument Descriptions
   :widths: 20 80
   :header-rows: 1

   * - --host
     - IP address the worker listens on
   * - --port
     - Port for RPC server (must match `agent_pools`)
   * - --agent_name
     - Unique name of this agent
   * - --workflow_types
     - Comma-separated workflow types supported by this worker

Step 3: Submit a DAG Task
-------------------------

Use the client dispatch script:

.. code-block:: bash

    python dispatch_task.py --master_addr "127.0.0.1:5002"

The script will:
- Submit the DAG via HTTP
- Host matches task `workflow_type` with the appropriate agent from `agent_pools`
- Agent executes the task and returns status/results
