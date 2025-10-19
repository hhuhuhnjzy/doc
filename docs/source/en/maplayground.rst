Maze Workflow Playground 可视化界面
==================================

Maze Workflow Playground 是一个基于 Web 的零代码可视化工作流编排平台，构建于 :doc:`maclient_api` 之上。它允许用户通过图形化界面创建会话、注册任务、设计工作流、提交执行并实时查看结果，无需编写任何代码即可完成复杂任务流程的构建与管理。

核心特性
--------

- **零代码操作**：通过拖拽或表单配置方式定义任务和依赖关系。
- **动态任务注册**：支持在线编写 Python 任务函数并即时注册使用。
- **任务包上传**：可上传 ZIP 格式的任务包，扩展系统能力。
- **实时执行监控**：提交后可查看任务状态、日志和输出结果。
- **多会话隔离**：每个浏览器会话对应独立的 MazeClient 实例，互不干扰。
- **内置任务库**：自动加载服务端预定义任务，开箱即用。

界面概览.. _playground:

Maze Workflow Playground — Visual Interface
===========================================

Maze Workflow Playground is a web-based, zero-code visual workflow orchestration platform built on top of :doc:`maclient_api`. It enables users to create sessions, register tasks, design workflows, submit executions, and view results in real time—all without writing any code—making it easy to build and manage complex task pipelines through a graphical interface.

Core Features
-------------

- **Zero-Code Operation**: Define tasks and dependencies via drag-and-drop or form-based configuration.
- **Dynamic Task Registration**: Write Python task functions inline and register them instantly for use.
- **Task Package Upload**: Upload ZIP-formatted task packages to extend system capabilities.
- **Real-Time Execution Monitoring**: After submission, view task status, logs, and output results.
- **Multi-Session Isolation**: Each browser session corresponds to an independent MazeClient instance, ensuring complete isolation.
- **Built-in Task Library**: Automatically loads pre-defined server-side tasks for immediate use.

Interface Overview
------------------

Upon opening the Playground homepage (typically at ``http://<host>:8000/``), users will see the following main functional areas:

1. **Session Management**
   - Click "Create Session" to connect to a specified Maze server (default: ``127.0.0.1:6380``).
   - Each session generates a unique ``Session ID``, serving as the context identifier for subsequent operations.

2. **Task Management**
   - **Write Task**: Enter a Python function with the ``@task`` decorator in the code editor, then click "Register Task" to make it available in the current session.
   - **Upload Task**: Upload a ZIP package containing task definitions; the system automatically parses and registers them.
   - **Available Tasks List**: Displays all callable tasks in the current session (including built-in and user-registered), showing name, description, and input/output parameters.

3. **Workflow Designer**
   - **Create New Workflow**: Name the workflow and enter the design interface.
   - **Add Task Node**: Select a task from "Available Tasks", fill in input parameters and resource requirements, and add it as a node in the workflow.
   - **Dependency Configuration** (Future Support): Current version supports linear execution; explicit dependency wiring will be supported in future releases.
   - **Edit/Delete Tasks**: Modify or remove already-added tasks.

4. **Execution & Monitoring**
   - **Set Input Parameters**: Provide initial inputs for the head node (entry task) of the workflow.
   - **Submit Execution**: Choose an execution mode (``server`` or ``local``) and submit. The system returns a ``Run ID``.
   - **Run Instance List**: Displays all execution records in the current session. Click to view results, cancel tasks, or destroy instances.
   - **Result Viewing**: Click on a specific task to view its output, status, and execution logs (if supported by the backend).

Typical Usage Flow
------------------

1. **Create a Session**
   Enter the Maze server address and click "Create Session" to obtain a Session ID.

2. **Register or Select a Task**
   - If tasks are already available, select directly from "Available Tasks";
   - To define custom logic, click "Write Task" and register a function like:

     .. code-block:: python

        from maze.library.tasks.definitions import task

        @task(
            name="hello_task",
            description="A greeting task",
            task_type='cpu',
            input_parameters={"properties": {"name": {"type": "string"}}},
            output_parameters={"properties": {"greeting": {"type": "string"}}}
        )
        def hello_task(name: str) -> str:
            return f"Hello, {name}!"

3. **Create a Workflow**
   Click "Create New Workflow", and enter a name (e.g., ``GreetingFlow``).

4. **Add a Task**
   Select ``hello_task`` from the task list, set input parameters to ``{"name": "Alice"}``, and click "Add Task".

5. **Submit for Execution**
   Click "Submit Execution", choose the execution mode (recommended: ``server``), and the system begins running the workflow.

6. **View Results**
   In the "Run Instances" list, locate the corresponding Run ID. Click on the task node to see the output: ``{"greeting": "Hello, Alice!"}``.

Technical Architecture
----------------------

- **Frontend**: Pure HTML + JavaScript (no framework dependencies), lightweight and minimal.
- **Backend**: Fully relies on RESTful APIs provided by :doc:`maclient_api`.
- **Communication**: Directly calls ``/api/...`` endpoints from the browser to manage the full lifecycle of sessions, workflows, and tasks.
- **Security**: Sessions are fully isolated. No persistent storage is used; resources are either manually cleaned or automatically reclaimed upon timeout.

Use Cases
---------

- Rapidly validate task logic
- Enable non-developers to orchestrate automation workflows
- Teaching demonstrations and prototyping
- Debugging execution behavior of complex workflows

Access Method
-------------

After starting the MazeClient web service, the Playground can be accessed by default at:

.. code-block:: text

   http://localhost:8000/

> 💡 Tip: Ensure the Maze server (e.g., Redis + Maze Server) is running at the specified address; otherwise, session creation will fail.

Future Roadmap
--------------

- Support data passing and dependency wiring between tasks (DAG visualization)
- Add real-time streaming output of task execution logs
- Provide workflow template saving and reuse functionality
- Integrate a task marketplace for sharing and discovering tasks
--------

打开 Playground 首页（通常为 ``http://<host>:8000/``）后，用户将看到以下主要功能区域：

1. **会话管理区**
   - 点击“创建会话”按钮，连接到指定的 Maze 服务端（默认 ``127.0.0.1:6380``）。
   - 每个会话生成唯一的 ``Session ID``，作为后续操作的上下文标识。

2. **任务管理区**
   - **编写任务**：在代码编辑器中输入带 ``@task`` 装饰器的 Python 函数，点击“注册任务”即可在当前会话中使用。
   - **上传任务**：上传包含任务定义的 ZIP 包，系统自动解析并注册。
   - **可用任务列表**：自动展示当前会话中所有可调用的任务（包括内置和用户注册的），显示名称、描述、输入/输出参数。

3. **工作流设计器**
   - **新建工作流**：为工作流命名后进入编排界面。
   - **添加任务节点**：从“可用任务”中选择一个任务，填写输入参数、资源需求等，添加为工作流中的一个节点。
   - **任务依赖配置**（未来支持）：当前版本为线性执行，后续将支持显式依赖连线。
   - **编辑/删除任务**：支持对已添加任务进行修改或移除。

4. **执行与监控区**
   - **设置输入参数**：为工作流头节点（入口任务）设置初始输入。
   - **提交执行**：选择执行模式（``server`` 或 ``local``）后提交，系统返回 ``Run ID``。
   - **运行实例列表**：展示当前会话中所有运行记录，可点击查看任务结果、取消任务或销毁实例。
   - **结果查看**：点击具体任务可查看其输出、状态和执行日志（若后端支持）。

典型使用流程
--------------

1. **创建会话**
   输入 Maze 服务端地址，点击“创建会话”，获得 Session ID。

2. **注册或选择任务**
   - 若已有任务，可直接从“可用任务”中选用；
   - 若需自定义逻辑，点击“编写任务”，粘贴如下代码并注册：

     .. code-block:: python

        from maze.library.tasks.definitions import task

        @task(
            name="hello_task",
            description="打招呼任务",
            task_type='cpu',
            input_parameters={"properties": {"name": {"type": "string"}}},
            output_parameters={"properties": {"greeting": {"type": "string"}}}
        )
        def hello_task(name: str) -> str:
            return f"Hello, {name}!"

3. **创建工作流**
   点击“新建工作流”，输入名称（如 ``GreetingFlow``）。

4. **添加任务**
   从任务列表选择 ``hello_task``，填写输入参数 ``{"name": "Alice"}``，点击“添加任务”。

5. **提交执行**
   点击“提交执行”，选择模式（推荐 ``server``），系统开始运行。

6. **查看结果**
   在“运行实例”中找到对应 Run ID，点击任务节点即可看到输出：``{"greeting": "Hello, Alice!"}``。

技术架构
--------

- **前端**：纯 HTML + JavaScript（无框架依赖），轻量简洁。
- **后端**：完全依赖 :doc:`maclient_api` 提供的 RESTful 接口。
- **通信**：通过浏览器直接调用 ``/api/...`` 接口，实现会话、工作流、任务的全生命周期管理。
- **安全性**：每个会话独立隔离，无持久化存储，关闭页面后资源可手动清理或超时回收。

适用场景
--------

- 快速验证任务逻辑
- 非开发人员编排自动化流程
- 教学演示与原型设计
- 调试复杂工作流的执行行为

访问方式
--------

启动 MazeClient Web 服务后，默认可通过以下地址访问 Playground：

.. code-block:: text

   http://localhost:8000/

> 💡 提示：确保 Maze 服务端（如 Redis + Maze Server）已在指定地址运行，否则会话创建将失败。


后续计划
--------

- 支持任务间数据传递与依赖连线（DAG 可视化）
- 增加任务执行日志实时流式输出
- 提供工作流模板保存与复用功能
- 集成任务市场，支持任务共享与发现