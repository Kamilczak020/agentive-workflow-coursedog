from typing import List
from haystack import component

@component
class ResultSplitter:
    @component.output_types(result_1=str, result_2=str, result_3=str)
    def run(self, results: List[str]):
        return {f"result_{i+1}": result for i, result in enumerate(results[:3])}
