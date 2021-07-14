import requests
from bs4 import BeautifulSoup
import urllib.parse
import os.path
import sys
from optparse import OptionParser
from datetime import datetime
import re

#we only crawl urls starts with https://www.eventbrite.com/e/


outputDir = "output"
urlDir = 'urls'
startTime = ''

startURL = 'https://www.eventbrite.com/d/online/all-events/'

startURL = 'https://eventsget.com/events/type/all/all-events-united-states/'

startURLs = []
startURLs.append('https://www.meetup.com/find/us--ca--san-jose')
startURLs.append('https://www.meetup.com/find/us--ca--san-francisco')
startURLs.append('https://www.meetup.com/find/us--ca--los-angeles')
startURLs.append('https://www.meetup.com/find/us--ny--new-york')
startURLs.append('https://www.meetup.com/find/us--wa--seattle')
startURLs.append('https://www.meetup.com/find/us--or--portland')
startURLs.append('https://www.meetup.com/find/us--fl--miami')
startURLs.append('https://www.meetup.com/find/us--ma--boston')
startURLs.append('https://www.meetup.com/find/us--dc--washington')
startURLs.append('https://www.meetup.com/find/us--nv--las-vegas')


# startURL = 'https://www.eventbrite.com/d/online/outdoor-concert/'

#filter rule for website www.eventbrite.com
def shouldVisit(url):
	if 'https://www.eventbrite.com/e/' == url or 'https://www.eventbrite.com/e' == url:
		return False
	if 'https://www.eventbrite.com/e/' in url or 'www.eventbrite.com/e/'in url:
		return True
	if url in startURLs:
		return True
	return False

#filter rule for website www.eventsget.com
def shouldVisit2(url):
	if 'https://eventsget.com/events/view/united-states' in url or 'eventsget.com/events/view/united-states'in url:
		return True
	if url in startURLs:
		return True
	return False


def shouldVisit3(url):
	if "meetup.com" not in url:
		return False
	if 'events' in url:
		x = re.search("[0-9]{9}", url)
		if x:
			return True
		trail = url.split("events")[-1]
		if len(trail) > 3:
			return True
	if url in startURLs:
		return True
	return False



crawledInfile = []



def printCurrentTime():
	from datetime import datetime

	# datetime object containing current date and time
	now = datetime.now()
	 
	#print("now =", now)

	# dd/mm/YY H:M:S
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
	print("date and time =", dt_string)	

def start(maxPageNumber, validPageNumber):
	global startTime
	now = datetime.now()
 
	

	# dd/mm/YY H:M:S
	dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
	startTime = dt_string
	print('startTime', startTime)

	urlsToCrawl = startURLs
	websiteName = startURLs[0].split('www')[-1].split('com')[0]
	websiteName = websiteName.replace(".", "")
	websiteName = websiteName.split('https://')[-1]
	print("websiteName", websiteName)
	visited = []
	if not os.path.isdir(outputDir):  # check if the directory exists
		os.mkdir(outputDir)  # if it doesnt then make it
	os.chdir(outputDir)
	if not os.path.isdir(urlDir):  # check if the directory exists
		os.mkdir(urlDir)
	pagesCrawled = 0
	while pagesCrawled < maxPageNumber and len(urlsToCrawl) > 0:
		print("pagesCrawled", pagesCrawled)
		print("urlsToCrawl", len(urlsToCrawl))
		print("valid", len(crawledInfile))
		printCurrentTime()
		if len(crawledInfile) > validPageNumber:
			print("we have got enough valid pages")
			break
		if urlsToCrawl[0] in visited:
			print("we seen this page before, we move on")
			urlsToCrawl.pop(0)
			continue
		# if not shouldVisit(urlsToCrawl[0]):
		# 	print("we skip non event urls", urlsToCrawl[0])
		# 	urlsToCrawl.pop(0)
		# 	continue
		try:
			print("fetching page ", urlsToCrawl[0])
			source_code = requests.get(urlsToCrawl[0])
			html = source_code.text  # get source code
			soup = BeautifulSoup(html, 'html.parser') 
		except:
			print("we cant parse current page, we should move on", urlsToCrawl[0])
			urlsToCrawl.pop(0)
			continue
		try:
			name = soup.title.string
			name = name.replace("\n", "")
			name = name.replace("\r", "")
			name = name.replace("\t", "")
			name = name.replace("|", "")
			name = name.replace(":", "")
			name = name.strip(' ')
		except:
			name = "no title " + str(pagesCrawled)
		fileName = "{0}.txt".format(name)
		if not os.path.isfile(fileName):
			try:
				writeToOutput(html, urlsToCrawl, fileName, websiteName)
			except Exception as e:
				print("we have error write page to file {}".format(e))
			
		else:
			print("we already saved crawled page{}".format(urlsToCrawl[0]))
			
			# dupFileName = name + "_dup_" + str(pagesCrawled) + ".txt"
			# writeToOutput(html, urlsToCrawl, dupFileName)
			# if checkIfTwoFileHasSameSize(fileName, dupFileName):
			# 	os.remove(dupFileName)
		#print("current page url", urlsToCrawl[0])
		visited.append(urlsToCrawl[0])
		pagesCrawled += 1
		neighbors = []
		for link in soup.findAll('a', href=True):
			link['href'] = urllib.parse.urljoin(urlsToCrawl[0], link['href'])
			if link['href'] not in visited:
				if '.pdf' not in link['href'] and '.jpg' not in link['href']:
					if 'javascript' not in link['href']:
						if 'css' not in link['href']:
							neighbors.append(link['href'])
							if 'meetup.com' in link['href']:
								urlsToCrawl.append(link['href'])
		checkCrawedURLs(urlsToCrawl, websiteName)
		# print("neighbors for current url", neighbors)
		# print("iterations:", pagesCrawled)
		size_of_directory = get_tree_size(os.curdir) / 1000000000
		print(round(size_of_directory, 5), "GB")
		print('\n')
		urlsToCrawl.pop(0)

	print("visited urls", visited)




def get_tree_size(path):
	"""Return total size of files in given path and subdirs."""
	total = 0
	for entry in os.scandir(path):
		if entry.is_dir(follow_symlinks=False):
			total += get_tree_size(entry.path)
		else:
			total += entry.stat(follow_symlinks=False).st_size
	return total


def checkCrawedURLs(urlsToCrawl, websiteName):
	urlFileName = "./{0}/{1}_urlsToCrawl.txt".format(urlDir, websiteName)
	with open(urlFileName, "w") as f:
		f.seek(0) 
		f.truncate()
		for url in urlsToCrawl:
			f.write("%s\n" % url)

	for url in urlsToCrawl:
		writeToOutput("", [url], "", websiteName)


def writeToOutput(html, urls, fileName, websiteName):
	global crawledInfile
	if not shouldVisit3(urls[0]):
		print("we skip non event urls", urls[0])
		return
	if urls[0] in startURLs:
		return
	# fo = open(fileName, "w")
	# fo.write('<page_url href=\"' + urls[0] + '\"></page_url>\n' + html)
	# fo.close()
	# size = os.stat(fileName)
	# size = size.st_size
	# if size == 0:
	# 	os.remove(fileName)
	# else:
	crawledInfile.append(urls[0])

	urlFileName = "./{0}/{1}_visitedURLs_total.txt".format(urlDir, websiteName)
	if os.path.exists(urlFileName):
		append_write = 'a' # append if already exists
	else:
		append_write = 'w' # make a new file if not

	if os.path.exists(urlFileName):
		with open(urlFileName) as myfile:
	    	 if urls[0] in myfile.read():
	        	 print('we seen this url already')
	        	 return


	with open(urlFileName, append_write) as f:
		f.write("%s" % urls[0])



	newUrlFileName = "./{0}/{1}_visitedURLs_{2}.txt".format(urlDir, websiteName, startTime)
	if os.path.exists(newUrlFileName):
		append_write = 'a' # append if already exists
	else:
		append_write = 'w' # make a new file if not
	with open(newUrlFileName, append_write) as f:
		f.write("%s" % urls[0])	

def checkIfTwoFileHasSameSize(fileName1, fileName2):
	size1 = os.stat(fileName1)
	size1 = size1.st_size

	size2 = os.stat(fileName2)
	size2 = size2.st_size
	return size1 == size2

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


# with open('/Users/hwen/Downloads/Archive/output/urls/meetup_urlsToCrawl.txt', "r") as f:
# 	currentUs = f.readlines()
# 	os.chdir(outputDir)
# 	for url in currentUs:
# 		writeToOutput("", [url], "", 'meetup_new')
# fileN = '/Users/hwen/Downloads/Archive/output/urls/meetup_new_visitedURLs_.txt'
# print(file_len(fileN))

# sys.exit(0)


if __name__ == '__main__':
	parser = OptionParser(usage="python newCrawler.py --max maxPagesCrawlered")
	parser.add_option("--valid", dest="valid", help="required number of valid pages")
	parser.add_option("--max", dest="max", help="max number of page to crawl")

	(options, args) = parser.parse_args()


	if not options.max:
		options.max = 100000	
	start(int(options.max), int(options.valid))
