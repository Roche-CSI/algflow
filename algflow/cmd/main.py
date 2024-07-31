import tomlkit as tomllib
from pathlib import Path
from contextlib import chdir

import typer
from typing import Optional, List
from rich import print
from rich.panel import Panel

from algflow.cmd.templates import ALG_TEMPLATE, PROJECT_TEMPLATE, HANDLER_PLUGIN_PROJECT_TEMPLATE, \
    HANDLER_PLUGIN_STARTER_TEMPLATE, PIPELINE_PLUGIN_STARTER_TEMPLATE, \
    PIPELINE_PLUGIN_PROJECT_TEMPLATE, PROJECT_HELPER_MESSAGE
from algflow.pipeline.main import AlgFlowPipeline
from typing_extensions import Annotated

from algflow.pipeline.simple_executor import SimplePipelineExecutor

app = typer.Typer()


def variable_to_class_name(name: str):
    return name.replace('_', ' ').title().replace(' ', '')


@app.command()
def run(inputs: Annotated[Optional[List[str]], typer.Option()],
        outputs: Annotated[Optional[List[str]], typer.Option()],
        output_file: Annotated[str, typer.Option()],
        yaml: Optional[str] = None):
    print(inputs, outputs, output_file, yaml)
    if yaml:
        pipeline = AlgFlowPipeline.create_from_yaml(yaml)
    else:
        pipeline = AlgFlowPipeline.create(inputs, outputs, output_file)
    #pipeline.dag.show()
    SimplePipelineExecutor(pipeline).execute()


def write_algorithm_starter(alg_file: str, alg_klass: str):
    #    alg_path.mkdir(exist_ok=True)
    with open(f"{alg_file}.py", "w") as f:
        f.write(ALG_TEMPLATE.format(alg_klass=alg_klass))


# TODO: SUPPORT creating algorithm file in user specified directory

@app.command()
def create_pipeline_plugin(name: str, description: Optional[str] = ""):
    if not description:
        description = "Pipeline Plugin for AlgFlow"
    path = Path(f"algflow-{name}-pipeline-plugin")
    path.mkdir(exist_ok=True)
    with chdir(path):
        Name = name.capitalize()
        with open(f"pyproject.toml", "w") as f:
            f.write(PIPELINE_PLUGIN_PROJECT_TEMPLATE.format(name=name, description=description,
                                                            Name=Name))

        with open(f"{name}_pipeline_plugin.py", "w") as f:
            f.write(PIPELINE_PLUGIN_STARTER_TEMPLATE.formate(name=name, Name=Name))


@app.command()
def add_algorithm(name: str):
    with open("pyproject.toml", "a") as f:
        data = tomllib.load(f)
        alg_name = name.capitalize()
        filename = name.lower()
        path = f"algorithms.{filename}.{alg_name}"
        data["options.entry_points.algflow.algorithms"][name] = path

    with open("pyproject.toml", "w") as f:
        tomllib.dump(data, f)
    write_algorithm_starter(alg_name, filename)


@app.command()
def create_project(name: str, alg_name: str = "hello"):
    pkg_name = f"algflow_{name}"
    name = f"algflow-{name}"
    path = Path(name)
    path.mkdir(exist_ok=True)
    with chdir(path):
        with open("pyproject.toml", "w") as f:
            alg_klass = variable_to_class_name(alg_name)
            f.write(PROJECT_TEMPLATE.format(name=name,
                                            pkg_name=pkg_name,
                                            alg_name=alg_name,
                                            alg_klass=alg_klass))
            pkg_path = Path(pkg_name)
            pkg_path.mkdir(exist_ok=True)
            with chdir(pkg_path):
                write_algorithm_starter(alg_name, alg_klass)

    print(Panel.fit(f"Project [bold red]{name}[/bold red] created.."))
    msg = PROJECT_HELPER_MESSAGE.format(name=name, pkg_name=pkg_name, alg_name=alg_name)
    print(msg)


@app.command()
def create_handler_plugin(name: str, ext: Optional[str] = "", description: Optional[str] = ""):
    if not description:
        description = "Data Handler for {ext} files"
    if ext:
        path = Path(f"algflow-{name}-{ext}-data-handler")
    else:
        path = Path(f"algflow-{name}-data-handler")
    path.mkdir(exist_ok=True)
    with chdir(path):
        Name = name.capitalize()
        ext = ext or name
        Ext = ext.capitalize()

        with open(f"pyproject.toml", "w") as f:
            f.write(HANDLER_PLUGIN_PROJECT_TEMPLATE.format(name=name, ext=ext,
                                                           description=description, Name=Name,
                                                           Ext=Ext))

        with open(f"{name}_{ext}_handler.py", "w") as f:
            f.write(HANDLER_PLUGIN_STARTER_TEMPLATE.format(name=name, ext=ext, Name=Name, Ext=Ext))


@app.command()
def check_documentation():
    pass

if __name__ == '__main__':
    app()
