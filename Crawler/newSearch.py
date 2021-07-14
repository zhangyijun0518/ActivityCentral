import sys

from whoosh import highlight
from whoosh import qparser
from whoosh.index import open_dir
from whoosh.scoring import TF_IDF, BM25F
from optparse import OptionParser


def start(searchTerm, operationType):
	if(operationType =="AND"):
		op_type = qparser.AndGroup
	elif(operationType=="OR"):
		op_type = qparser.OrGroup
	else:
		op_type = qparser.AndGroup
	dirname = "indexdir"
	ix = open_dir(dirname)
	qp = qparser.MultifieldParser(['content', 'path', 'title', 'head1', 'head2', 'head3', 'head4'], ix.schema,
								  group=op_type)
	qp.add_plugin(qparser.PlusMinusPlugin)
	query = qp.parse(searchTerm)
	#print('query', query)
	#define search mode
	w = BM25F(B=0.75, K1=1.5)
	with ix.searcher(weighting=w) as searcher:
		results = searcher.search(query, terms=True)
		results.fragmenter = highlight.ContextFragmenter(maxchars=50, surround=50, )
		found_doc_num = results.scored_length()
		print("found_doc_num", found_doc_num)
		run_time = results.runtime
		if found_doc_num == 0:
			final_top_output = "Sorry " + str(found_doc_num) + " Search Results Found." \
				"Search Results for "+searchTerm+" using BM25F (" + str(run_time) + " seconds)\n"
		else:
			final_top_output = "We found " + str(found_doc_num) + " Search Results" \
				" for " +searchTerm+ " using BM25F Ranking and '"+ operationType+\
							   "' operation to score (" + str(run_time) + " seconds)"
		print("final_top_output", final_top_output)
		print('\n')
		if results:
			for hit in results:
				snip = hit.highlights('content', top=2)
				path = hit['path']
				title = hit['title']
				score = hit.score
				score = path + "   (Score: " + str(score) + ")"
				print(str(title.encode('utf-8')), '\n', str(score.encode('utf-8')))
				print("snapshot", snip)    
if __name__ == '__main__':
	parser = OptionParser(usage="python newSearch.py --term searchTerm --type")
	parser.add_option("--term", dest="term", help="searchTerm")
	parser.add_option("--type", dest="type", help="operationType")
	(options, args) = parser.parse_args()
	if not options.type:
		options.type = 'AND'
	print('searchTerm', options.term)
	start(options.term, options.type)
