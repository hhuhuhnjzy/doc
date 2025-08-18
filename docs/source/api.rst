Maze API Reference
==================

This section lists Maze's core APIs.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Name
     - Description
   * - ``task_node = maze.create_node(task_func, config)``
     - Creates a task node using the user-defined task function and configuration parameters (such as file, tool, model settings, and resources), and returns a node object that encapsulates its unique identifier and associated metadata.
   * - ``ok = maze.remove_node(node_id)``
     - Removes the specified node from the build graph given its ``node_id`` and returns a boolean acknowledgment of success.
   * - ``workflow = maze.create_workflow(nodes, edges)``
     - Creates a workflow from a node list and an edge list where each edge is a tuple ``(source_node_id, target_node_id)``, snapshots the resulting DAG, and returns a workflow object with a unique id.
   * - ``resource = maze.predict_resource(workflow_id)``
     - Given a ``workflow_id``, produces an estimated resource usage summary object for the workflow based on per-node declarations.
   * - ``maze.submit(workflow_id)``
     - Submits the workflow identified by ``workflow_id`` to the distributed scheduler for execution.
   * - ``status = maze.get(workflow_id)``
     - Retrieves the latest execution state and results for the specified ``workflow_id`` and returns a status object with per-task information.
