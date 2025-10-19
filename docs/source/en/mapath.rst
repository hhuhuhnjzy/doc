.. _mapath:

mapath: MaPath — Task-Level Dynamic Adaptive Scheduler for Maze
===============================================================

The ``mapath`` module implements the core scheduling engine of the Maze framework—**MaPath (Multi-agent Path Scheduler)**—responsible for decomposing user-submitted LLM Agent workflows (expressed as DAGs) into fine-grained tasks and efficiently, robustly scheduling them across heterogeneous compute clusters.
The design goal of MaPath is: **to maximize cluster resource utilization and system throughput while ensuring low latency**.

Core Concept
------------

Unlike traditional frameworks that treat an entire agent as a scheduling unit (e.g., AutoGen, AgentScope), MaPath adopts a **task-level scheduling** architecture:

- Each workflow is modeled as a **DAG (Directed Acyclic Graph)**, with nodes representing tasks and edges representing data dependencies.
- The scheduler allocates resources, executes, and monitors at the **individual task** level.
- Tasks can be scheduled across different nodes, supporting heterogeneous resource requirements (CPU, GPU, I/O).

This fine-grained scheduling enables Maze to:
- Achieve more flexible **load balancing**
- Avoid blocking an entire agent due to a single long-running task
- Significantly reduce P95 response time under high load (Paper Figure 6b)

Scheduling Algorithm: DAPS (Dynamic Adaptive Priority Scheduling)
------------------------------------------------------------------

MaPath employs the **DAPS algorithm** to dynamically compute task priorities. The priority score of each ready task is a weighted sum of two components:

.. math::
   \text{Score} = w_1 \cdot \text{Urgency} + w_2 \cdot \text{Criticality}

where the default weights are: :math:`w_1 = 2.0`, :math:`w_2 = 1.0`.

- **Urgency**: Reflects the urgency based on the number of remaining inference tasks in the workflow
  :math:`\text{Urgency} = 1 - \frac{\text{remaining\_inferences}}{\text{max\_known\_inferences}}`

- **Criticality**: Reflects the proportion of this task in the total workflow execution time
  :math:`\text{Criticality} = \frac{\text{pred\_exec\_time}}{\text{expected\_dag\_time}}`

> **Note**: `pred_exec_time` is provided by the :ref:`malearn` module; `expected_dag_time` is estimated from the average execution time of historically similar workflows.

The priority queue is ordered by `(submission_time, -Score, enqueue_sequence)`, ensuring **high-score tasks are prioritized**, **FIFO fairness**, and **no starvation**.

System Architecture
-------------------

The MaPath scheduler consists of three cooperating threads (see `daps.py`):

1. **DAG Creator**
   - Receives user-submitted workflows (in JSON format) from a memory queue
   - Reconstructs the DAG structure using `networkx`
   - Pre-registers each task via `TaskStatusManager.add_task()`
   - Enqueues tasks with zero in-degree into the scheduling queue

2. **Scheduler & Submitter**
   - Pops the highest-priority task from the priority queue
   - Checks if the task has been cascade-canceled (e.g., due to predecessor failure)
   - Invokes `TaskScheduler.submit()` to dispatch the task to the Ray cluster for execution

3. **Monitor**
   - Listens for task completion notifications (from execution nodes)
   - Updates task status and execution time
   - Triggers **Cascade Cancel** for failed tasks to avoid wasted computation
   - Upon completion of all tasks in a DAG, records total execution time and cleans up memory

Resource Awareness and Context Management
-----------------------------------------

MaPath achieves resource-aware scheduling through `DAGContextManager` (see `dag_context.py`):

- Creates a `DAGContext` Ray Actor for each running DAG
- The context stores: DAG ID, preferred execution node, configuration parameters (e.g., model cache path, API keys)
- The scheduler uses `get_least_loaded_node()` to select the least-loaded available node
- Supports task affinity binding to specific nodes, reducing data transfer overhead

Integration with Other Maze Modules
-----------------------------------

- **With `malearn`**: Retrieves predicted execution times for DAPS scoring
- **With `TaskScheduler`**: Handles actual task dispatching and execution
- **With `TaskStatusManager`**: Maintains unified task state management (PENDING / RUNNING / FINISHED / FAILED / CANCELLED)
- **With `MaRegister`**: Rapidly constructs DAGs using predefined tool templates

Performance Advantages (from the Paper)
---------------------------------------

In dynamic load experiments (Figure 6), MaPath demonstrates significant advantages:

- **P95 Latency**: Under 125% overload, Maze-V (with MaPath) achieves only 285 seconds, while AutoGen exceeds 1400 seconds
- **Throughput**: Maze completes 51 DAGs (1.02 DAG/min), outperforming AutoGen (0.88) and AgentScope (0.86)
- **GPU Utilization**: Average GPU memory utilization reaches over 60%, compared to only 25% in agent-level frameworks

These results demonstrate that MaPath’s task-level scheduling effectively mitigates task backlog and improves resource efficiency.

Configuration Parameters
------------------------

- ``w1``: Weight for urgency (default: 2.0)
- ``w2``: Weight for criticality (default: 1.0)
- ``max_known_inferences``: Historical maximum number of inference tasks (used to normalize Urgency)
- ``task_type_avg_times``: Default execution times for each task type (used as fallback during cold start)

These parameters can be adjusted at scheduler startup via command-line arguments or configuration files.

Related References
------------------

- **Paper**: *Maze: Efficient Scheduling for LLM Agent Workflows* (ASPLOS '26)
- **Section 5**: Distributed Scheduler (MaPath architecture)
- **Algorithm 2**: Pseudocode for the DAPS scheduling algorithm
- **Figure 6**: Comparison of response time and resource utilization under dynamic load
- **Appendix E.4**: Analysis of task-level scheduling overhead (average scheduling overhead is only 0.0043 seconds)