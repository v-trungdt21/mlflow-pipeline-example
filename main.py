import click
import json
import git
import yaml


import mlflow
from mlflow.utils import mlflow_tags
from mlflow.entities import RunStatus
from mlflow.utils.logging_utils import eprint

from mlflow.tracking.fluent import _get_experiment_id

from rich import print

mlflow.set_experiment("test_pipeline")


def _already_ran(
    step_folder, entry_point_name, parameters, git_commit, experiment_id=None
):
    """Best-effort detection of if a run with the given entrypoint name,
    parameters, and experiment id already ran. The run must have completed
    successfully and have at least the parameters provided.
    """
    experiment_id = experiment_id if experiment_id is not None else _get_experiment_id()
    client = mlflow.tracking.MlflowClient()
    all_run_infos = reversed(client.list_run_infos(experiment_id))
    for run_info in all_run_infos:
        full_run = client.get_run(run_info.run_id)
        # print(full_run)
        tags = full_run.data.tags
        cur_run_entry_point_name = tags.get(
            mlflow_tags.MLFLOW_PROJECT_ENTRY_POINT, None
        )
        cur_run_source_fullname = tags.get(mlflow_tags.MLFLOW_SOURCE_NAME, None)
        if cur_run_entry_point_name is None or cur_run_source_fullname is None:
            continue
        cur_run_source_name = cur_run_source_fullname.split("/")[-1]
        if (
            cur_run_source_name != step_folder.split("/")[-1]
            or cur_run_entry_point_name != entry_point_name
        ):
            continue
        # if tags.get(mlflow_tags.MLFLOW_PROJECT_ENTRY_POINT, None) != entry_point_name:
        #     continue
        match_failed = False
        for param_key, param_value in parameters.items():
            query_value = full_run.data.params.get(param_key)
            try:
                run_value = (
                    type(param_value)(query_value) if query_value is not None else None
                )
            except ValueError:
                run_value = None
            # print(f"Current run value for key {param_key}: {run_value}")
            if run_value != param_value:
                match_failed = True
                break
        if match_failed:
            continue

        if run_info.to_proto().status != RunStatus.FINISHED:
            eprint(
                (
                    "Run matched, but is not FINISHED, so skipping "
                    "(run_id=%s, status=%s)"
                )
                % (run_info.run_id, run_info.status)
            )
            continue

        previous_version = tags.get(mlflow_tags.MLFLOW_GIT_COMMIT, None)
        if git_commit != previous_version:
            eprint(
                (
                    "Run matched, but has a different source version, so skipping "
                    "(found=%s, expected=%s)"
                )
                % (previous_version, git_commit)
            )
            continue
        return client.get_run(run_info.run_id)
    eprint("No matching run has been found.")
    return None


# TODO(aaron): This is not great because it doesn't account for:
# - changes in code
# - changes in dependant steps
def _get_or_run(step_folder, entrypoint, parameters, git_commit, use_cache=True):
    if use_cache and git_commit is None:
        raise Exception(
            f"Please define git commit hash if want to use cache in {step_folder}.{entrypoint}"
        )
    existing_run = _already_ran(step_folder, entrypoint, parameters, git_commit)
    if use_cache and existing_run:
        print(
            "Found existing run for %s.entrypoint=%s and parameters=%s"
            % (step_folder, entrypoint, parameters)
        )
        return existing_run
    print(
        "Launching new run for %s.entrypoint=%s and parameters=%s"
        % (step_folder, entrypoint, parameters)
    )
    submitted_run = mlflow.run(step_folder, entrypoint, parameters=parameters)
    return mlflow.tracking.MlflowClient().get_run(submitted_run.run_id)


@click.command()
@click.option("--something", type=str)
def workflow(something):
    print("Main pipeline param:", something)

    with open("pipeline.yaml", "r") as stream:
        try:
            pipeline = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    print(pipeline)

    with mlflow.start_run() as active_run:
        # this get the parent git commit run only
        # git_commit = active_run.data.tags.get(mlflow_tags.MLFLOW_GIT_COMMIT)
        pipeline_runs = []

        for pipe, obj in pipeline["pipeline"].items():
            r = _get_or_run(
                obj["step_folder"],
                obj["entrypoint"],
                obj["params"],
                obj["git_commit"] if "git_commit" in obj else None,
                obj["use_cache"],
            )
            pipeline_runs.append(r)
        with open(
            "/home/termanteus/workspace/mlops/playground/pipeline/output/prj2.json", "r"
        ) as js:
            obj = json.load(js)
        obj["main"] = [something]
        with open(
            "/home/termanteus/workspace/mlops/playground/pipeline/output/final.json",
            "w",
        ) as js:

            json.dump(obj, js)


if __name__ == "__main__":
    workflow()
