.. _malearn:

malearn: Machine Learning-Based Execution Time Prediction Module for the Maze Framework
======================================================================================

The ``malearn`` module provides a lightweight, extensible, and online-learning-capable system for predicting task execution times in the Maze scheduling framework (ASPLOS '26).
Designed specifically for heterogeneous tasks within LLM agent workflows—such as text reasoning, vision-language processing, speech recognition, etc.—this module leverages machine learning models to accurately estimate task durations, thereby enabling Maze's **DAPS scheduling algorithm** (Dynamic Priority Scheduling based on task urgency and criticality).

Design Goals
------------

Accurate execution time prediction is foundational to efficient DAG scheduling in the Maze framework. The core design principles of ``malearn`` include:

- **Multimodal Feature Modeling**: Different task types (e.g., LLM, VLM, Speech) use custom-tailored feature sets.
- **Incremental Learning Capability**: As new task execution data accumulates, models can be automatically updated in the background, continuously improving prediction accuracy.
- **Robustness Assurance**: Supports outlier filtering, default value imputation for missing features, and falls back to heuristic estimation when models are unavailable.
- **Persistence Support**: Models and training data are automatically persisted to disk, enabling quick recovery after service restarts and facilitating offline analysis and debugging.

Core Components
---------------

ExecTimePredictor: Task-Type-Specific Predictors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: malearn.ExecTimePredictor
   :members:
   :undoc-members:
   :show-inheritance:

Each ``ExecTimePredictor`` instance is dedicated to a single tool type, independently maintaining its model, normalizer, and dataset.

Currently supported task types and their features include:

- **``llm_process``**: Large language model inference tasks
  Features: ``text_length`` (text length), ``token_count`` (number of tokens), ``batch_size``, ``reason`` (whether chain-of-thought reasoning is used)

- **``vlm_process``**: Vision-language model tasks (e.g., image QA, image-text generation)
  Features: Image height/width/area/aspect ratio, image entropy, edge density, text region proportion, brightness mean and variance, prompt length and token count, etc.

- **``llm_fuse2In1``**: Dual-text fusion tasks (e.g., comparison, summarization)
  Features: Lengths and token counts of two input texts, prompt information, ``reason`` flag

- **``speech_process``**: Speech processing tasks (e.g., speech recognition)
  Features: ``duration`` (audio duration), ``audio_entropy``, ``audio_energy``

By default, an **XGBoost regression model** is used (consistent with the "tree-based online learner" described in the paper), but MLP regressors and linear regression are also supported for comparative experiments or lightweight deployments.

DAGTaskPredictor: Unified Interface for the Scheduler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: malearn.DAGTaskPredictor
   :members:
   :undoc-members:
   :show-inheritance:

This is the primary entry point invoked by the Maze scheduler, responsible for:

1. **Function Name Mapping**: Maps function names in DAG nodes (e.g., ``"vlm_inference_v1"``) to standard tool types (e.g., ``"vlm_process"``)
2. **Feature Aggregation**: Reads results from all predecessor tasks in Redis and extracts precomputed features (``succ_task_feat``) for the current task
3. **Execution Prediction**: Invokes the corresponding ``ExecTimePredictor`` to estimate execution time
4. **Safety Fallback**: If the model is untrained or prediction fails, falls back to heuristic defaults (e.g., 15 seconds for GPU tasks, 3 seconds for CPU tasks, 1 second for I/O tasks)

This design ensures that Maze can make reasonable scheduling decisions during cold starts, under sparse data conditions, or in the event of model failures.

Integration with the Maze Framework
-----------------------------------

Within Maze workflows, each completed task writes the following information to Redis (key: ``result:<task_id>``):

- ``start_time`` / ``end_time``: Timestamps marking task start and end
- ``curr_task_feat``: Input features of the current task
- ``succ_task_feat``: Precomputed feature mappings for each successor task

The ``DAGTaskPredictor.collect_data_for_task()`` method consumes these logs:

- Computes actual execution time (``end_time - start_time``)
- Appends features and execution time to the corresponding tool-type CSV dataset
- When the number of new samples reaches a threshold, **triggers incremental training in a background thread**

Prediction results are directly fed into the DAPS scheduler (Algorithm 2 in the paper) to compute task **Criticality** and **Urgency**, ultimately determining the task’s priority in the scheduling queue.

Extending to New Task Types
---------------------------

To support a new task type (e.g., ``"video_process"``), follow these three steps:

1. Add the new type and its feature list to ``ExecTimePredictor.tool_types``
2. Add a mapping from function name to tool type in ``DAGTaskPredictor.func_name_to_tool_type``
3. Ensure the task execution logic outputs the corresponding ``curr_task_feat`` in its logs

All models and data are stored independently under the directory structure ``<model_dir>/<tool_type>/``, ensuring isolation and modularity.

Related References
------------------

- **Paper**: *Maze: Efficient Scheduling for LLM Agent Workflows* (ASPLOS '26)
- **Appendix E.1**: Theoretical analysis of execution time prediction (based on second-order Taylor expansion and XGBoost regularization)
- **Figure 2(c)**: Resource consumption characteristics across different task types (CPU/GPU/I/O intensive)
- **DAPS Scheduling Algorithm** (Algorithm 2 in the paper): How predicted time influences task priority