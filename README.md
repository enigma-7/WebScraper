 # WebScraper
Dependencies: os, PyPDF2, json, time, selenium

This project is intended to be used as a resource management tool for arXiv pre-print documents. 

The class arxivScraper within scraper.py is composed of three broad categories of sequences, specifically: 
1. Constructing numerically ordered indexing system from a given **resource directory** of arxiv documents and thereafter, extracting hyperlinks from either the PDF documents (pre arXiv naming convention change) or from the document names (post arXiv naming convention change). [Refer to https://arxiv.org/help/arxiv_identifier for more info].
2. Webcrawling through relevant arXiv pages to scrape: (1) URL, (2) Title, (3) Author/s, (4) Abstract, and (5) Bibtex entry and storing results in .json files within the **response directory**. 
3. Writing resource management summaries and bibtex files with relevant formatting in place to the **bibliography directory**. 

defaults.py is self-explanatory. 
