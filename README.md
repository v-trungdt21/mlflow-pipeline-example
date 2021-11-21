# Project prep
1. Each project (e.g: a part of a pipeline) should prepare:
  - `conda.yaml`: conda environment information (can get by running: conda env export --name ENVNAME > conda.yml). Highly recommend write it yourself if you can.
  - MLproject:
    - Define entrypoint: running a specific file with predefined parameters.
    - Point to the correct `conda.yaml` path
2. Modify `main.py` of root folder (`main` of pipeline): Notice that pipeline code can be everywhere, you just need to set the correct folder path for the projects:
  - `main.py`: should contain the logic of the pipeline (which pipeline run first, what to do after each run,...)
  - `pipeline.yaml`: should contain name, repo_folder, entrypoint (set in MLproject of corresponding prj), params of the entrypoint,...

# Run
- If the main pipeline can be use by your running conda env, use this command (exclude it if you want to create new env for it)
- On the very first run, mlflow should create each conda env for each project; install the dependencies and run as the pipeline's defined.

```
cd <pipeline_dir>
mlflow run . --no-conda [-P <param_name>=<param_val> --experiment-name <exp_name> <other mlflow run params...>]
````