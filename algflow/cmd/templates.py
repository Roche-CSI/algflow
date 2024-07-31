ALG_TEMPLATE = """`from algflow import Algorithm
from traits.api import Int, Float, Array

class {alg_klass}(Algorithm):
    class Param:
        pass

    class Input:
        pass

    class Output:
        pass

    def run(self, inputs, outputs):
        pass
"""

PROJECT_TEMPLATE = """[project]
    name = "{name}"
    version = "0.0.1"
    description = "project description here"
    authors = [
        {{name = "Your Name", email = "developer@example.com"}},
    ]
    requires-python = ">= 3.11"
    dependencies = [
        "algflow",
    ]
    readme = "README.md"
    keywords = ["algflow", "pipeline", "algorithm"]

        
[project.entry-points."algflow.algorithms"]
    "{alg_name}" = "{pkg_name}.{alg_name}:{alg_klass}"

[tool.algflow]
    pkg_name = "{pkg_name}"
"""

PROJECT_HELPER_MESSAGE = """Starter algorithm can be found in [bold green]{pkg_name}/{alg_name}.py[/bold green].
    :star: Add more algorithms using [blue]algflow add-algorithm[/blue] command.
    :star: For adding existing algorithm, add an entry in "[bold blue]\[options.entry_points.algflow.algorithms][/bold blue] section in pyproject.toml"
    :star: Run the pipeline using [blue]algflow run[/blue] command."
"""

HANDLER_PLUGIN_PROJECT_TEMPLATE = """[project]
    name = "{name}-{ext}-handler"
    version = "0.0.1"
    description = "{description}"
    authors = [
        {{name = "Your Name", email = "developer@example.com"}},
    ]
    requires-python = ">= 3.11"
    dependencies = [
      "algflow",
    ]
    readme = "README.md"
    keywords = ["algflow", "plugin", "data handler", "storage backend"]

[project.entry-points."algflow.data_handlers"]
    "{ext}" = "{name}_{ext}_handler:{Name}{Ext}Handler"
"""

HANDLER_PLUGIN_STARTER_TEMPLATE = """from pathlib import Path
from typing import Dict, Any
from algflow import AlgFlowDataHandler, AlgFlowDataDescriptor, DataElements, PathSpec


class {Name}{Ext}Handler(AlgFlowDataHandler):
    pathspec = PathSpec(extension="{ext}", name_pattern="^.*$", content_type="text/plain")
    
    def __init__(self, path: str):
        self.path = Path(path) if not isinstance(path, Path) else path
        # Add your initialization code
        
        
    def elements(self) -> DataElements:
        pass
        
    def get(self, *args: str) -> Dict[str, Any]:
        pass
        
    def set(self, name, value: Any):
        pass
    
    def query(self, name: str, query: Dict[str, Any]) -> Any:
        pass
"""

PIPELINE_PLUGIN_PROJECT_TEMPLATE = """[project]
    name = "{name}"
    version = "0.0.1"
    description = "{description}"
    authors = [
        {{name = "Your Name", email = "developer@example.com"}},
    ]
    requires-python = ">= 3.11"
    dependencies = [
      "algflow",
    ]
    readme = "README.md"
    keywords = ["algflow", "plugin", "pipeline", "hooks"]

[project.entry-points."algflow.pipeline_plugins"]
    "{name}" = "{name}_pipeline_plugin:{Name}PipelinePlugin"
"""


PIPELINE_PLUGIN_STARTER_TEMPLATE = """from algflow.pipeline import AlgFlowPipelinePlugin
from algflow.data.spec import AlgFlowDataDescriptor


class {Name}PipelinePlugin(AlgFlowPipelinePlugin):
    name = "{name}"
    def before_run_algorithm(self, algorithm: Algorithm, inputs: Dict[str, Any]):
        pass
        
    def after_run_algorithm(self, algorithm: Algorithm, outputs: Dict[str, Any]):
        pass

"""