Running Baseline with HEFT / CPOP
=================================

This section introduces how to run Maze using traditional baseline scheduling algorithms such as HEFT and CPOP.

Step 1: Start the Master Node
-----------------------------

The master node receives DAG tasks, runs the selected scheduling algorithm, and distributes tasks to slaver nodes.

.. code-block:: bash

    python master_api.py --host "172.17.0.3" --port 5002 \
        --compute_nodes "172.17.0.3:5003,172.17.0.4:5003,172.17.0.5:5003,172.17.0.6:5003" \
        --scheduler_strategy "heft"

.. list-table:: Argument Descriptions
   :widths: 20 80
   :header-rows: 1

   * - Argument
     - Description
   * - --host
     - The IP address the master listens on
   * - --port
     - Port the master listens on
   * - --compute_nodes
     - Comma-separated list of slaver node addresses
   * - --scheduler_strategy
     - Scheduling algorithm to use, either ``heft`` or ``cpop``

Step 2: Start Slaver Nodes
--------------------------

Run slaver_api.py on all computing nodes (including the master node, which also acts as a computing node).

.. code-block:: bash

    # Running on node 1
    python slaver_api.py --master_addr 172.17.0.3:5002 --host 172.17.0.3 --port 5003

    # Running on node 1
    python slaver_api.py --master_addr 172.17.0.3:5002 --host 172.17.0.4 --port 5003

.. list-table:: Argument Descriptions
   :widths: 20 80
   :header-rows: 1

   * - Argument
     - Description
   * - --master_addr
     - The Slaver needs to know the address of the Master in order to send a callback notification to it after the task is completed.
   * - --host
     - The IP address that the current Slaver node's service is listening on.
   * - --port
     - The port that the current Slaver node's service is listening on.

.. note::
   Adjust IP and port accordingly for each node.

Step 3: Dispatch a DAG Task
---------------------------

Run dispatch_task.py on any machine that has access to the master node to submit the task.

.. code-block:: bash

    python dispatch_task.py --master_addr "172.17.0.3:5002"

.. list-table:: Argument Descriptions
   :widths: 20 80
   :header-rows: 1

   * - Argument
     - Description
   * - --master_addr
     - Tell the client where the API address of the master is in order to submit the task to the past.

