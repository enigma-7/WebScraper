import scraper, defaults, os

if __name__=="__main__":
    scraper = scraper.arxivScraper()
    scraper.write_summary(verbose=False)
    scraper.write_ref_bib(verbose=False)
    # bibdir = defaults.directory["Bibliography"]
    # os.system("pdflatex %s -output-directory=%s"%(bibdir + "/summary.tex", bibdir + "/summary.pdf"))
