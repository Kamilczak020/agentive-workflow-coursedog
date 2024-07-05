from haystack import component

from tools.search_semantically import run_semantic_search

@component
class SemanticSearch:
  """
  A component performing semantic search based on the provided data
  """
  @component.output_types(results=list[dict])
  def run(self, arguments):
      return {
          'results': run_semantic_search(arguments)
      }

