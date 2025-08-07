Running Maze Core Framework
===========================

This section describes how to run the core components of the Maze/AgentOS framework, including setting up Redis, Ray, and launching the resource/scheduler layers.

Step 1: Start Ray Cluster
-------------------------

Ray is used for distributed task execution.

.. code-block:: bash

    # Start Ray on the head node
    ray start --head

    # Start Ray on a worker node and connect to head
    ray start --address='head_node_ip:head_node_port'

Step 2: Start Redis
-------------------

Redis is used for message passing and lightweight data storage.

.. code-block:: bash

    # Start Redis on port 6380 (non-protected mode)
    redis-server --port 6380 --bind 0.0.0.0 --protected-mode no &

.. note::
   On lab node10, Redis is already configured via Docker. Use `docker ps` to check.

Step 3: Start Resource Layer
----------------------------
AgentOS is divided into a resource layer and a scheduling layer, which need to be started in sequence.The resource layer is responsible for managing and providing underlying computing resources.

.. code-block:: bash

    cd AgentOS/src/agentos/resource
    python api_server.py --redis_ip 127.0.0.1 --redis_port 6380 --flask_port 5000

Step 4: Start Scheduler Layer
-----------------------------
The scheduling layer is responsible for receiving tasks and performing intelligent scheduling according to strategies.

.. code-block:: bash

    cd AgentOS/src/agentos/scheduler
    python scheduler.py --master_addr 127.0.0.1:5000 --redis_ip 127.0.0.1 --redis_port 6380 --strategy mlq --flask_port 5001

Step 5: Dispatch a Demo Task
----------------------------
Once all services are started, you can run a sample to verify that the system is working properly.

.. code-block:: bash

    cd AgentOS/src/agentos/scheduler
    python dispatch_task.py
