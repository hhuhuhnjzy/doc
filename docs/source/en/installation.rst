.. _installation:

Installation Guide
==================

This guide provides detailed instructions on how to install the Maze framework and its dependencies in a local environment. To ensure a smooth installation process, we recommend **installing in steps**: first manually installing core dependencies that are sensitive to system environments (such as PyTorch), then using `pip` to install the remaining dependencies in bulk.

Maze is built on Python 3.11. We strongly recommend using a virtual environment to avoid dependency conflicts.

Step 1: Create and Activate a Virtual Environment (Recommended)
----------------------------------------------------------------

We highly recommend creating an isolated Python virtual environment using `venv` or `conda`:

.. code-block:: bash

   # Create a virtual environment using venv
   python -m venv maze-env
   source maze-env/bin/activate    # Linux/macOS
   # maze-env\Scripts\activate     # Windows

After activation, your command-line prompt will typically display `(maze-env)`.

Step 2: Manually Install PyTorch and Related Libraries
-----------------------------------------------------

According to the official `requirements.txt`, the following packages contain platform-specific binaries and are **not recommended to be installed directly via `requirements.txt`**:

- ``torch==2.6.0``
- ``torchvision==0.21.0``

Please select the appropriate installation command based on your operating system, and whether you have an NVIDIA GPU (and its CUDA version).

**If you have an NVIDIA GPU and want to enable GPU acceleration:**

Visit `https://pytorch.org/get-started/locally/ <https://pytorch.org/get-started/locally/>`_ to get the latest command. For example, at the time of writing, the command for Linux + CUDA 11.8 is:

.. code-block:: bash

   pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu118

**If you are using a CPU-only environment (no GPU or CPU only):**

.. code-block:: bash

   pip install torch==2.6.0+cpu torchvision==0.21.0+cpu --index-url https://download.pytorch.org/whl/cpu

> .. note::
>    Always visit the PyTorch official website to get the installation command that matches your system. An incorrect version may lead to poor performance or runtime failures.

Step 3: Install Other Third-party Dependencies
---------------------------------------------

Now you can safely install the remaining dependencies. Most of these packages are pure Python or provide universal binary distributions (wheels), ensuring high installation success rates.

1. Make sure you are in the project root directory (the directory containing `requirements.txt`).
2. Run the following command:

.. code-block:: bash

   pip install -r requirements.txt

This command will automatically install all required third-party libraries from the Tsinghua mirror (`pypi.tuna.tsinghua.edu.cn`), including FastAPI, Flask, Ray, Transformers, EasyOCR, and more.

> .. warning::
>    If you skip Step 2 and run this command directly, you may end up with an incompatible version of `torch` (e.g., CPU version overwriting GPU version), resulting in significantly reduced performance.

Step 4: Install the Maze Project Itself
---------------------------------------

Install Maze in editable mode (`-e`) for development and debugging, which also registers the `maze` command-line tool:

.. code-block:: bash

   pip install -e .

After installation, verify it with the following command:

.. code-block:: bash

   maze --help

If help information is displayed correctly, Maze has been successfully installed.

Step 5: Configure Project Path (Required for Server Mode)
---------------------------------------------------------

If you plan to use **server mode** (distributed execution), you must modify the configuration file:

1. Open ``config/config.toml``.
2. Locate the ``[paths]`` section and change ``project_root`` to the **absolute path** of your Maze project on your local machine:

   .. code-block:: toml

      [paths]
      project_root = "/your/absolute/path/to/Maze"

> .. important::
>    This step is critical. The Ray cluster needs this path to distribute code to all worker nodes. An incorrect path will cause remote nodes to fail to locate the code, leading to execution failure.

Optional Step: Download Sample Models
-------------------------------------

If you wish to run built-in example workflows that depend on local models (such as EasyOCR or Hugging Face models), run the following script to download model caches:

.. code-block:: bash

   python maze/utils/download_model.py

This will download the required model files into the ``model_cache/`` directory.

Troubleshooting
---------------

- **`torch` installation fails?**
  Check your network connection or try switching to the official PyTorch mirror. Avoid using domestic mirrors for `torch` installation, as they may be out of sync.

- **`pip install -r requirements.txt` fails?**
  Ensure `torch` and `torchvision` are successfully installed. Verify your Python version is 3.11.

- **`maze` command not found?**
  Confirm that `pip install -e .` was executed and the virtual environment is activated.

After completing the above steps, your Maze environment is ready. Proceed to :ref:`quick_start` to begin your first distributed Agent workflow.