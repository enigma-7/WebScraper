import os, PyPDF2, json, time, defaults
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

class arxivScraper:
	def __init__(self, filedir = defaults.directory["Resource"],
						respdir = defaults.directory["Response"],
						 bibdir  = defaults.directory["Bibliography"]):
		self.filedir = filedir
		self.respdir = respdir
		self.bibdir  = bibdir
		self.filenames  = self.get_filenames()
		self.filepaths  = self.get_filepaths()
		self.arxivids   = self.get_arxivids()
		self.hyperlinks = self.get_hyperlinks()

	def is_arxiv(self, fil):
		digits = [str(i) for i in range(10)]
		if(fil[0] in digits):
			return True
		else:
			return False

	def is_pre2000(self, fil):
		if int(fil[0]) >= 4:
			return True
		else:
			return False

	def get_filenames(self):
		"""From resource directory: searches for files named numerically; sorts based on release date."""
		eligibles = list(filter(self.is_arxiv, os.listdir(self.filedir)))
		eligibles.sort()

		pre2000 = list(filter(lambda f:     self.is_pre2000(f), eligibles))
		pos2000 = list(filter(lambda f: not self.is_pre2000(f), eligibles))
		sorted = pre2000 + pos2000

		return sorted

	def get_filepaths(self):
		"""Get aboslute file paths"""
		return [os.path.abspath(self.filedir + fil) for fil in self.filenames]

	def get_arxivids(self):
		"""Get arXiv IDs from filenames."""
		return [fil.split('.pdf')[0].split('v')[0] for fil in self.filenames]

	def get_hyperlinks(self):
		"""Gets hyperlinks from either the first hyperlink encountered in PDF (pre NCC) or
		constructs URL from filename (post NCC)."""
		url = []

		for fil in self.filenames:
			fillen = fil.split('.').__len__()
			if fillen == 2:
				pdf = PyPDF2.PdfFileReader(self.filedir + fil).pages[0]
				url.append(pdf['/Annots'][0].getObject()['/A']['/URI'])
			else:
				url.append('https://arxiv.org/abs/' + fil.split('.pdf')[:-1][0])

		print("Hyperlink list constructed	\n")
		return url

	def extract(self):
		"""Webcrawler using Firefox to scrape relevant elements from hyperlinks given into response directory"""
		options = Options()
		options.add_argument('--headless')
		driver = webdriver.Firefox(options=options)

		for i, hyperlink in enumerate(self.hyperlinks):
			if not os.path.exists(self.respdir + self.arxivids[i] + '.json'):
				print(hyperlink)
				base = driver.get(hyperlink)

				try:
					url      = driver.find_element_by_css_selector(r'.arxividv > span:nth-child(1) > a:nth-child(1)').get_attribute('href')
					#doi      = driver.find_element_by_css_selector(r'.link-https').get_attribute('data-doi')
					title    = driver.title.split('] ')[-1]
					authors  = driver.find_element_by_xpath(r'/html/body/main/div/div/div[1]/div[3]/div/div[2]').text
					abstract = driver.find_element_by_xpath(r'/html/body/main/div/div/div[1]/div[3]/div/blockquote').text
					driver.find_element_by_link_text("Export citation").click()
					driver.find_element_by_xpath(r'//*[@id="arxiv"]').click()
					time.sleep(2)
					bibtex   = driver.find_element_by_css_selector(r'.modal-content > div:nth-child(3) > textarea:nth-child(2)').text

					scraped = {"url": url, "Title": title, "Authors": authors, "Abstract": abstract, "bibtex": bibtex}

					with open(self.respdir + self.arxivids[i] + '.json', 'w') as fp:
						json.dump(scraped, fp)

				except Exception:
					print(Exception)
					continue

		driver.quit()

	def check_new_files(self):
		"""Check for discrepancies between files is resource directory and files in response directory."""
		responses = [fil.split('.json')[0] for fil in list(filter(self.is_arxiv, os.listdir(self.respdir)))]
		new_files = (set(self.arxivids) - set(responses)).__len__()

		if new_files != 0:
			print('New files found: \n')
			self.extract()

	def write_summary(self, sep = defaults.separator, verbose = False, title_len = defaults.title_len):
		"""Loads .json files and writes resource management summary."""
		self.check_new_files()

		f = open(self.bibdir + 'summary.txt', 'w')
		f.write(sep.join(["arXiv", "Title", "Authors"]) + "\n")

		if verbose:
			print("Resource Manager Output:		\n")

		for i in range(self.arxivids.__len__()):

			arxivid = self.arxivids[i]
			filepath = self.filepaths[i]

			with open('responses/' + arxivid + '.json') as json_file:
				data = json.load(json_file)

			#Prevent math errors in LaTeX compilation
			split = data['Title'].split("] ")[-1].split(" ")
			for j, str in enumerate(split):
				if "_" in str:
					split[j] = "$" + str.split("_")[0] + "_{" +  str.split("_")[-1] + "}$"

			title    = " ".join(split)[:title_len]
			url      = data['url']
			#Write last names only.
			authors  = ", ".join([str.split(" (")[0].split(" ")[-1].split(")")[-1] for str in data['Authors'].split(",")])

			line     = sep.join([r"\href{file:%s}{%s}" % (filepath,arxivid),
									r"\href{%s}{%s}"% (url, title),
										authors + "    \n"])

			f.write(line)

			if verbose:
				print("\t" + line[:-3])

		f.close()

	def write_ref_bib(self, verbose = False):
		"""Loads .json files and writes ref.bib file."""
		self.check_new_files()

		f = open(self.bibdir + 'ref.bib', 'w')

		print("\n")

		if verbose:
			print("Bibtex output:")

		for i, arxivid in enumerate(self.arxivids):

			with open(self.respdir + arxivid + '.json') as json_file:
				data = json.load(json_file)

			bibtex = data['bibtex']
			#Use arXiv ID as bibtex key.
			split1 = bibtex.split('{')
			split2 = split1[1].split(',')
			split2[0] = arxivid
			split1[1]  = ','.join(split2)

			bibtex = '{'.join(split1)

			f.write(bibtex)

			if verbose:
				print("\t" + bibtex)

		f.close()
