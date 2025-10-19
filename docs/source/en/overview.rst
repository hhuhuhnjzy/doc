.. _overview:

Project Overview
================

Maze is a **distributed execution framework** specifically designed for **Large Language Model Agents (LLM Agent)** applications. It aims to address the performance bottlenecks and low resource utilization issues faced by current LLM Agents in high-concurrency and complex task scenarios. As the capabilities of large models continue to grow, intelligent agents are transitioning from single-machine experiments to production-level deployments, placing higher demands on system scalability, execution efficiency, and operational capabilities. Maze achieves efficient scheduling and distributed execution of complex agent workflows through innovative architectural design.

Core Challenges
---------------

Traditional LLM Agent frameworks (such as LangChain, AutoGPT, etc.) typically adopt an "Agent-Level Deployment" model, where the entire Agent instance is deployed as a single unit on a single computing node. This approach has several critical issues:

- **Resource Bottlenecks**: An Agent may simultaneously include CPU-intensive, GPU-intensive, and I/O-intensive tasks, leading to resource contention and limiting overall throughput.
- **Uneven Load Distribution**: Some nodes might become overloaded due to running complex agents while others remain idle, resulting in wasted resources.
- **Poor Scalability**: It's challenging to achieve linear performance improvement by merely adding more nodes.

Maze Solutions
--------------

To address these challenges, Maze introduces a revolutionary "Task-Level Deployment" architecture. Its core idea is to break down complex agent workflows into a series of fine-grained tasks based on dependency relationships to form Directed Acyclic Graphs (DAG). These tasks are dynamically distributed by a central scheduler to different computing nodes within the cluster for parallel execution.

This design brings three significant advantages:

1. **Efficient Load Balancing**
   Maze can perceive each task's resource requirements (CPU, GPU, memory) and real-time load conditions of each node, allowing for precise task scheduling. For example, it schedules model inference tasks to GPU nodes and data processing tasks to CPU nodes, maximizing cluster resource utilization.

2. **Strong Scalability**
   The system adopts a decentralized execution model, supporting near-linear performance improvements with the addition of compute nodes through efficient task distribution mechanisms. Business growth can be accommodated simply by horizontally scaling Worker nodes.

3. **Excellent Usability**
   Users do not need to be experts in distributed systems. Through simple Python APIs and `@tool` decorators, developers can define tasks and orchestrate workflows just like writing standalone programs. Maze automatically handles task serialization, code distribution, dependency resolution, and remote execution.

System Architecture
-------------------

Maze features a modular design consisting of four core components that work together to form a complete distributed agent management platform:

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - **Component**
     - **Function Description**

   * - **MaRegister (Registration Module)**
     - Responsible for defining the agent workflow. Users register task functions to the computation graph via Python APIs and specify dependencies between tasks (DAG).

   * - **MaLearn (Learning Module)**
     - An online learning model predicting task complexity (e.g., execution time) based on historical execution data, providing intelligent decision-making support for the scheduler. Experiments show that Maze achieves optimal balance between prediction accuracy and training efficiency using XGBoost combined with incremental learning.

   * - **MaPath (Routing/Scheduling Module)**
     - The smart scheduling core of the framework implements the DAPS (DAG-Aware Predictive Scheduling) algorithm. MaPath considers task priorities, dependencies, resource needs, and data affinity to dynamically decide task execution locations.

   * - **MaWorker (Execution Module)**
     - Deployed on each computing node as the execution engine, responsible for receiving dispatch instructions, executing tasks, managing runtime environments, and reporting status.

Operating Modes
---------------

Maze supports two operating modes to flexibly adapt to development and production scenarios:

- **Local Mode**
  No need to start central services or Ray clusters; workflows execute locally in independent threads, suitable for quick development and debugging.

- **Server Mode**
  Built on a Ray-based distributed execution environment, supporting multi-node collaboration, ideal for high-concurrency, large-scale task processing in production environments.

Application Scenarios
---------------------

Maze is especially suitable for the following scenarios:

- Multi-step, long-running LLM Agent workflows (e.g., automated report generation, intelligent customer service processes)
- Heterogeneous task mixed execution (e.g., text generation + image recognition + database queries)
- High availability, high concurrency enterprise AI applications

Through Maze, developers can easily build high-performance, scalable distributed intelligent agent systems, unleashing the full potential of large models in real production environments.