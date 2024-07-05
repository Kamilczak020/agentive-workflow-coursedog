from haystack import component

from tools.cypher_query import run_cypher_query

@component
class CypherQuery:
  """
  A component running a neo4j cypher query 
  """
  @component.output_types(results=list[dict])
  def run(self, arguments):
      return {
          'results': run_cypher_query(arguments)
      }

