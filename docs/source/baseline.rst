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

Run the following on **each compute node**, including the master:

.. code-block:: bash

    python slaver_api.py --master_addr 172.17.0.3:5002 --host 172.17.0.3 --port 5003

.. note::
   Adjust IP and port accordingly for each node.

Step 3: Dispatch a DAG Task
---------------------------

From any client machine:

.. code-block:: bash

    python dispatch_task.py --master_addr "172.17.0.3:5002"
