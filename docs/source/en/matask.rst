.. _built_in_tasks:

Maze Built-in Task Library
==========================

Maze provides a rich set of **predefined tasks (Built-in Tasks)** covering common scenarios such as file I/O, PDF processing, OCR, text analysis, and workflow control. These tasks are registered using the ``@task`` decorator and can be directly invoked in :doc:`maclient_api` or :doc:`maplayground` without additional development.

All built-in tasks reside in the ``maze.library.tasks`` module and are organized into submodules by functionality:

- ``io_tasks``: File and data loading
- ``pdf_tasks``: PDF document processing
- ``image_tasks``: Image and OCR processing
- ``llm_tasks``: Large language model interaction
- ``control_tasks``: Flow control and aggregation

Below is a detailed overview of commonly used tasks, grouped by function.

File and Data Loading Tasks
---------------------------

.. _task-load_pdf:

``load_pdf``
~~~~~~~~~~~~
- **Description**: Loads a PDF file from a local path and returns its binary content.
- **Inputs**:
  - ``pdf_path`` (str): Full path to the PDF file.
- **Outputs**:
  - ``pdf_content`` (bytes): Binary content of the PDF.
- **Use Case**: Serves as the starting point for PDF processing pipelines, loading the file into memory for downstream tasks.

.. _task-count_lines:

``count_lines``
~~~~~~~~~~~~~~~
- **Description**: Counts the number of lines in the first uploaded text file.
- **Inputs**:
  - ``supplementary_files`` (dict): File dictionary automatically injected by the framework.
- **Outputs**:
  - ``line_count`` (int): Total number of lines in the file.
- **Use Case**: Quickly validates data scale; commonly used in data pre-checks.

PDF Text and Structure Extraction Tasks
---------------------------------------

.. _task-extract_text_and_tables_from_native_pdf:

``extract_text_and_tables_from_native_pdf``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- **Description**: Rapidly extracts text and structured tables from **native (non-scanned) PDFs**.
- **Inputs**:
  - ``pdf_content`` (bytes): Binary content of the PDF.
- **Outputs**:
  - ``extracted_text`` (str): Formatted text and table content, separated by page.
- **Limitation**: **Not suitable for scanned or image-based PDFs**.
- **Dependency**: ``pdfplumber``
- **Use Case**: Efficiently parses selectable-text PDFs such as e-books, reports, and academic papers.

PDF Rasterization and OCR Tasks
-------------------------------

.. _task-extract_text_from_pdf_range:

``extract_text_from_pdf_range``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- **Description**: Renders specified page ranges of a PDF to images and performs **OCR recognition**, suitable for scanned documents.
- **Inputs**:
  - ``pdf_content`` (bytes): Binary content of the PDF.
  - ``page_range`` (list[int]): Start and end page numbers (e.g., ``[3, 5]``, 1-indexed).
- **Outputs**:
  - ``extracted_text`` (str): OCR-recognized text, annotated by page.
- **Dependencies**: ``PyMuPDF (fitz)`` + ``EasyOCR`` (supports Chinese and English)
- **Resource Requirement**: Requires GPU (``gpu_mem=4096``)
- **Use Case**: Processes scanned PDFs, image-only documents, or PDFs with non-copyable text.

.. _task-ocr_memory_chunk:

``ocr_memory_chunk``
~~~~~~~~~~~~~~~~~~~~
- **Description**: Performs OCR on a small in-memory PDF chunk (e.g., 5 pages) and returns a list of text per page.
- **Inputs**:
  - ``pdf_chunk_content`` (bytes): Binary content of a small PDF chunk.
- **Outputs**:
  - ``all_text_parts`` (List[str]): List of OCR results, one per page.
- **Use Case**: Atomic unit in a parallel OCR pipeline; enables chunked processing of large documents.

Document Structure and Workflow Control Tasks
---------------------------------------------

.. _task-calculate_page_offset:

``calculate_page_offset``
~~~~~~~~~~~~~~~~~~~~~~~~~
- **Description**: Calculates the **page offset** based on the logical TOC page numbers and the actual physical starting page of Chapter 1.
- **Inputs**:
  - ``logical_toc_with_ranges`` (dict): Table of contents with page ranges, parsed by an LLM.
  - ``physical_page_of_chapter_1`` (int): Actual starting page number of Chapter 1.
- **Outputs**:
  - ``page_offset`` (int): Offset value (physical page = logical page + offset).
- **Use Case**: Resolves mismatches between TOC page numbers and actual content pages; provides basis for chapter segmentation.

.. _task-split_pdf_by_chapters:

``split_pdf_by_chapters``
~~~~~~~~~~~~~~~~~~~~~~~~~
- **Description**: **Splits a PDF into multiple independent files by chapter** based on a structured TOC and page offset.
- **Inputs**:
  - ``pdf_content`` (bytes)
  - ``logical_toc_with_ranges`` (dict)
  - ``page_offset`` (int)
  - ``physical_page_of_chapter_1`` (int)
  - ``output_directory`` (str)
- **Outputs**:
  - ``pdf_chunk_paths`` (List[str]): File paths of saved chapter PDFs.
- **Use Case**: Automates chapter splitting for books or reports, enabling per-chapter downstream processing.

.. _task-scatter_chapter_in_memory:

``scatter_chapter_in_memory``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- **Description**: Splits a single chapter PDF into multiple small chunks (binary streams) in memory based on page count.
- **Inputs**:
  - ``chapter_pdf_content`` (bytes)
  - ``pages_per_chunk`` (int, default 5)
- **Outputs**:
  - ``page_chunk_contents`` (List[bytes]): List of binary PDF chunks.
- **Use Case**: Provides chunked input for parallel OCR or summarization tasks.

Text Aggregation and Summary Preparation Tasks
----------------------------------------------

.. _task-gather_ocr_results:

``gather_ocr_results``
~~~~~~~~~~~~~~~~~~~~~~
- **Description**: **Flattens** a nested list of OCR text results from multiple parallel tasks into a single list of page texts.
- **Inputs**:
  - ``ocr_texts`` (List[List[str]])
- **Outputs**:
  - ``flat_page_texts_list`` (List[str])
- **Use Case**: Aggregates distributed OCR results and restores the original page order.

.. _task-split_text_for_summary:

``split_text_for_summary``
~~~~~~~~~~~~~~~~~~~~~~~~~~
- **Description**: Re-groups a list of page texts into **summary chunks** (by specified page count) for parallel LLM summarization.
- **Inputs**:
  - ``flat_page_texts_list`` (List[str])
  - ``pages_per_summary_chunk`` (int, default 10)
- **Outputs**:
  - ``summary_text_chunks`` (List[str])
- **Use Case**: Addresses LLM context length limits, enabling segmented summarization of long documents.

Result Persistence Tasks
------------------------

.. _task-save_summary_to_md:

``save_summary_to_md``
~~~~~~~~~~~~~~~~~~~~~~
- **Description**: Saves a chapter summary to a Markdown file.
- **Inputs**:
  - ``summary_text`` (str)
  - ``output_directory`` (str)
  - ``chapter_title`` (str)
- **Outputs**:
  - ``summary_file_path`` (str)
- **Use Case**: Structured storage of results for readability and integration.

.. _task-assemble_final_report:

``assemble_final_report``
~~~~~~~~~~~~~~~~~~~~~~~~~
- **Description**: **Merges multiple chapter summary Markdown files** into a complete report in order.
- **Inputs**:
  - ``summary_md_paths`` (List[str])
  - ``book_title`` (str)
  - ``output_directory`` (str)
- **Outputs**:
  - ``final_report_path`` (str)
- **Use Case**: Generates final deliverables such as book summaries or compiled meeting notes.

Utility Tasks
-------------

.. _task-scan_chapters_directory:

``scan_chapters_directory``
~~~~~~~~~~~~~~~~~~~~~~~~~~~
- **Description**: Scans a directory and returns paths, titles, and page counts of all PDF chapter files.
- **Inputs**:
  - ``directory_path`` (str)
- **Outputs**:
  - ``chapters_info`` (List[dict])
- **Use Case**: Automatically discovers chapter files for batch processing pipelines.

.. _task-load_markdown_files:

``load_markdown_files``
~~~~~~~~~~~~~~~~~~~~~~~
- **Description**: Loads all `.md` summary files from a specified directory and returns a structured list.
- **Inputs**:
  - ``directory_path`` (str)
- **Outputs**:
  - ``chapter_summaries`` (List[dict]): Each entry contains ``title`` and ``content`` fields.
- **Use Case**: Provides data source for post-processing tasks such as report reassembly or content filtering.

Usage Recommendations
---------------------

- **Prefer native text extraction**: For PDFs with selectable text, use ``extract_text_and_tables_from_native_pdf`` — it is faster and more accurate.
- **Use OCR for scanned documents**: For image-based PDFs, always use ``extract_text_from_pdf_range`` or a chunked OCR approach.
- **Chunk large documents**: For chapters over 20 pages, use ``scatter_chapter_in_memory`` with parallel OCR to improve efficiency.
- **Persist results early**: Save critical intermediate results (e.g., OCR text, chapter PDFs) to disk to avoid memory overflow or redundant computation.

Extensibility and Customization
-------------------------------

All built-in tasks are standard Python functions. Users can:
- Reuse their logic for secondary development;
- Implement custom tasks by following their patterns;
- Upload enhanced versions via the ``upload_task`` API to override default behavior.

> 💡 Tip: The complete list of available tasks can be dynamically retrieved by calling the server's ``/api/tasks`` endpoint.