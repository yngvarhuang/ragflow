---
sidebar_position: -1
slug: /configure_knowledge_base
---

# Configure dataset

Most of RAGFlow's chat assistants and Agents are based on datasets. Each of RAGFlow's datasets serves as a knowledge source, *parsing* files uploaded from your local machine and file references generated in **File Management** into the real 'knowledge' for future AI chats. This guide demonstrates some basic usages of the dataset feature, covering the following topics:

- Create a dataset
- Configure a dataset
- Search for a dataset
- Delete a dataset

## Create dataset

With multiple datasets, you can build more flexible, diversified question answering. To create your first dataset:

![create dataset](https://raw.githubusercontent.com/infiniflow/ragflow-docs/main/images/create_knowledge_base.jpg)

_Each time a dataset is created, a folder with the same name is generated in the **root/.knowledgebase** directory._

## Configure dataset

The following screenshot shows the configuration page of a dataset. A proper configuration of your dataset is crucial for future AI chats. For example, choosing the wrong embedding model or chunking method would cause unexpected semantic loss or mismatched answers in chats. 

![dataset configuration](https://raw.githubusercontent.com/infiniflow/ragflow-docs/main/images/configure_knowledge_base.jpg)

This section covers the following topics:

- Select chunking method
- Select embedding model
- Upload file
- Parse file
- Intervene with file parsing results
- Run retrieval testing

### Select chunking method

RAGFlow offers multiple chunking template to facilitate chunking files of different layouts and ensure semantic integrity. In **Chunking method**, you can choose the default template that suits the layouts and formats of your files. The following table shows the descriptions and the compatible file formats of each supported chunk template:

| **Template** | Description                                                           | File format                                                                                   |
|--------------|-----------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| General      | Sequentially splits content to preserve semantic continuity across common layouts. | MD, MDX, DOCX, XLSX, XLS (Excel 97-2003), PPT, PDF, TXT, JPEG, JPG, PNG, TIF, GIF, CSV, JSON, EML, HTML |
| Q&A          | Maps question–answer pairs into retrievable units with optional categories. | XLSX, XLS (Excel 97-2003), CSV/TXT                                                             |
| Resume       | Enterprise edition only; parses resumes into structured fields for talent search.  | DOCX, PDF, TXT                                                                                |
| Manual       | Hierarchically splits user guides and manuals by headings and sections. | PDF                                                                                           |
| Table        | Converts rows into structured chunks using column headers for filterable search. | XLSX, XLS (Excel 97-2003), CSV/TXT                                                             |
| Paper        | Recognizes scholarly sections and splits by paragraph for precise retrieval. | PDF                                                                                           |
| Book         | Chunks long documents by chapter/section using heading hierarchy or TOC. | DOCX, PDF, TXT                                                                                |
| Laws         | Splits legal texts by article/section and preserves numbering for precise lookup. | DOCX, PDF, TXT                                                                                |
| Presentation | Chunks slides page-by-page and can include images for multimodal retrieval. | PDF, PPTX                                                                                     |
| Picture      | Extracts text and key elements from images via OCR/vision for searchable chunks. | JPEG, JPG, PNG, TIF, GIF                                                                      |
| One          | Treats the whole document as a single chunk to preserve full context.                    | DOCX, XLSX, XLS (Excel 97-2003), PDF, TXT                                                      |
| Tag          | Serves as a tag dictionary for other datasets.             | XLSX, CSV/TXT                                                                                 |

#### 各模板示例

- Q&A
  - Model/file‑type notes: Use CSV/TXT with clear headers; one Q&A per row.
  - CSV example:
    ```csv
    question,answer,category
    How do I reset my password?,Go to Settings → Security → Reset Password.,Account
    How to request an invoice?,Sign in to the enterprise portal and submit a request.,Finance
    ```

- Table
  - Model/file‑type notes: First row as header; each row becomes a chunk; multi‑value fields can use delimiters (e.g., `;`).
  - CSV example:
    ```csv
    id,title,content,tags
    1001,Account Security,Password strength and two-factor authentication,security;auth
    1002,Invoice Issuance,Workflow and required fields,finance;invoice
    ```

- Laws
  - Model/file‑type notes: Keep consistent numbering (Chapter/Article). Prefer DOCX/TXT or searchable PDF.
  - Text example:
    ```text
    Chapter I General Provisions
    Article 3 A contract is established according to law …
    ```

- Presentation
  - Model/file‑type notes: PPTX text should be in text boxes; PDFs with one slide per page are preferred; images can be extracted for multimodal search.
  - PPTX example:
    ```text
    Slide 1: Quarterly Report
    - Revenue up 12%
    - Key initiatives: A, B, C
    ```

- Picture
  - Model/file‑type notes: OCR/vision extracts text and key elements; ensure readable resolution; avoid glare and shadows.
  - Example:
    `invoice.jpg` with vendor name, date, and total captured by OCR.

- Resume (Enterprise)
  - Model/file‑type notes: Prefer text‑based DOCX/PDF (scans should be OCRed first).
  - Example (fields extracted):
    ```json
    {"name":"John Doe","email":"john@doe.com","education":"B.Sc. 2015–2019","experience":"Software Engineer 2019–2024","skills":"Python, SQL"}
    ```

- Manual
  - Model/file‑type notes: PDFs with clear heading hierarchy; content is chunked by section.
  - Text example:
    ```text
    1. Getting Started
    1.1 Installation
    1.2 Configuration
    ```

- Paper
  - Model/file‑type notes: Use searchable PDFs; typical sections (Abstract, Methods, Results) are recognized.
  - Text example:
    ```text
    Abstract — We propose …
    Methods — We collected …
    Results — The model …
    ```

- Book
  - Model/file‑type notes: DOCX with Heading 1/2/3 styles or PDFs with a valid TOC are preferred.
  - Text example:
    ```text
    Chapter 2: The Basics
    Section 2.1: Introduction
    ```

- Tag
  - Model/file‑type notes: At least two columns (e.g., `tag`, `keywords`). Used by other datasets.
  - CSV example:
    ```csv
    tag,keywords
    Security,password;permission;auth
    Finance,invoice;expense;tax
    ```

You can also change a file's chunking method on the **Datasets** page.

![change chunking method](https://raw.githubusercontent.com/infiniflow/ragflow-docs/main/images/embedded_chat_app.jpg)

### Select embedding model

An embedding model converts chunks into embeddings. It cannot be changed once the dataset has chunks. To switch to a different embedding model, you must delete all existing chunks in the dataset. The obvious reason is that we *must* ensure that files in a specific dataset are converted to embeddings using the *same* embedding model (ensure that they are compared in the same embedding space).

The following embedding models can be deployed locally:

- BAAI/bge-large-zh-v1.5
- maidalun1020/bce-embedding-base_v1

:::danger IMPORTANT
These two embedding models are optimized specifically for English and Chinese, so performance may be compromised if you use them to embed documents in other languages.
:::

### Upload file

- RAGFlow's **File Management** allows you to link a file to multiple datasets, in which case each target dataset holds a reference to the file.
- In **Knowledge Base**, you are also given the option of uploading a single file or a folder of files (bulk upload) from your local machine to a dataset, in which case the dataset holds file copies. 

While uploading files directly to a dataset seems more convenient, we *highly* recommend uploading files to **File Management** and then linking them to the target datasets. This way, you can avoid permanently deleting files uploaded to the dataset. 

### Parse file

File parsing is a crucial topic in dataset configuration. The meaning of file parsing in RAGFlow is twofold: chunking files based on file layout and building embedding and full-text (keyword) indexes on these chunks. After having selected the chunking method and embedding model, you can start parsing a file:

![parse file](https://raw.githubusercontent.com/infiniflow/ragflow-docs/main/images/parse_file.jpg)

- As shown above, RAGFlow allows you to use a different chunking method for a particular file, offering flexibility beyond the default method. 
- As shown above, RAGFlow allows you to enable or disable individual files, offering finer control over dataset-based AI chats. 

### Intervene with file parsing results

RAGFlow features visibility and explainability, allowing you to view the chunking results and intervene where necessary. To do so: 

1. Click on the file that completes file parsing to view the chunking results: 

   _You are taken to the **Chunk** page:_

   ![chunks](https://raw.githubusercontent.com/infiniflow/ragflow-docs/main/images/file_chunks.jpg)

2. Hover over each snapshot for a quick view of each chunk.

3. Double-click the chunked texts to add keywords, questions, tags, or make *manual* changes where necessary:

   ![update chunk](https://raw.githubusercontent.com/infiniflow/ragflow-docs/main/images/add_keyword_question.jpg)

:::caution NOTE
You can add keywords to a file chunk to increase its ranking for queries containing those keywords. This action increases its keyword weight and can improve its position in search list.  
:::

4. In Retrieval testing, ask a quick question in **Test text** to double-check if your configurations work:

   _As you can tell from the following, RAGFlow responds with truthful citations._

   ![retrieval test](https://raw.githubusercontent.com/infiniflow/ragflow-docs/main/images/retrieval_test.jpg)

### Run retrieval testing

RAGFlow uses multiple recall of both full-text search and vector search in its chats. Prior to setting up an AI chat, consider adjusting the following parameters to ensure that the intended information always turns up in answers:

- Similarity threshold: Chunks with similarities below the threshold will be filtered. By default, it is set to 0.2.
- Vector similarity weight: The percentage by which vector similarity contributes to the overall score. By default, it is set to 0.3.

See [Run retrieval test](./run_retrieval_test.md) for details.

## Search for dataset

As of RAGFlow v0.20.5, the search feature is still in a rudimentary form, supporting only dataset search by name.

![search dataset](https://raw.githubusercontent.com/infiniflow/ragflow-docs/main/images/search_datasets.jpg)

## Delete dataset

You are allowed to delete a dataset. Hover your mouse over the three dot of the intended dataset card and the **Delete** option appears. Once you delete a dataset, the associated folder under **root/.knowledge** directory is AUTOMATICALLY REMOVED. The consequence is:

- The files uploaded directly to the dataset are gone;  
- The file references, which you created from within **File Management**, are gone, but the associated files still exist in **File Management**. 

![delete dataset](https://raw.githubusercontent.com/infiniflow/ragflow-docs/main/images/delete_datasets.jpg)
