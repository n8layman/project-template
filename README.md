
<!-- README.md is generated from README.Rmd. Please edit that file -->

# Containerised R workflow template

<!-- badges: start -->

[![Project Status: WIP – Initial development is in progress, but there
has not yet been a stable, usable release suitable for the
public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)
[![Lifecycle:
experimental](https://img.shields.io/badge/lifecycle-experimental-orange.svg)](https://lifecycle.r-lib.org/articles/stages.html#experimental)
[![container-workflow-template](https://github.com/ecohealthalliance/container-template/actions/workflows/container-workflow-template.yml/badge.svg)](https://github.com/ecohealthalliance/container-template/actions/workflows/container-workflow-template.yml)
[![License for Code:
MIT](https://img.shields.io/badge/License%20(for%20code)-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![License:
CC-BY-4.0](https://img.shields.io/badge/License%20(for%20text)-CC_BY_4.0-blue.svg)](https://creativecommons.org/licenses/by/4.0/)

<!-- badges: end -->

This repository is a project pipeline template

## Set-up and installation

This pipeline was created using R version 4.3.2 (2023-10-31 ucrt). This
project uses the {renv} framework to record R package dependencies and
versions. Packages and versions used are recorded in the `renv.lock`.

- Clone the repository
  - In the terminal enter
    `git clone https://github.com/ecohealthalliance/WABNET-analysis.git`
    in a suitable directory
- Duplicate the R environment used for the analysis:
  - This project was created using R version 4.3.2. This and other
    versions of R are available on the [R Archive
    Network](https://cloud.r-project.org/)
  - This project uses the {renv} framework to record R package
    dependencies and versions. Packages and versions used are recorded
    in the `renv.lock` file.
  - To install the {renv} package run `install.packages("renv")`
  - Run `renv::hydrate()` to copy whatever packages are already
    available in your user / site libraries into the project library
  - Run `renv::restore()` to install any remaining required packages
    into your project library.

## Targets workflow

The project pipeline has been automated using the the {targets} pipeline
management tool. {Targets} breaks down the analysis into a series of
discrete, skippable computational steps. Individual steps can be loaded
into memory using tar_load(target_name). An overview of the pipeline can
be found in the `_targets.R` file in the main project folder. Each
component, such as data ingest, is further broken out into its own
collection of targets as indicated in the `_targets.R` file.

Targets are organized into distinct groups, including:

1.  Data ingest targets
2.  Data processing targets
3.  Analysis targets
4.  Output targets

All targets are defined within the `_targets.R` file.

## Re-running computationally expensive targets

Some targets are computationally intensive and long-running. The output
of these targets has been saved in the `\data` folder as compressed RDS
files. These files end in ‘.gz’ and can be manually accessed using
`read_rds()` or automatically through the targets pipeline. By default
these steps will not be re-computed and are disconnected in the pipeline
DAG unless a flag is set in the `.env` file. A description of these
flags can be found at the top of the `_targets.R` and in the `.env`
file.

## Pipeline Overview

## Misc

A hook to prevent users from commiting files greater than GitHub’s 100Mb
file size limit is available in the `.githooks` folder. To enable this
copy the `.githooks/pre-commit` file to the `.git/hooks` directory by
running the following command in the terminal within the project base
directory

    cp .githooks/pre-commit .git/hooks/pre-commit

## Dockerized RStudio server

A dockerized container is available that provides a pre-configured
environment with RStudio Server, optimized for machine learning
workflows. It comes with {targets}, {tarchetypes}, {tidymodels},
{dbarts}, and {mgcv} pre-installed, enabling users to quickly build,
tune, and deploy predictive models without the hassle of configuring
dependencies or installing packages manually. The Dockerfile can be
built on both `arm64` and `x86` architectures.

A pre-built image for `x86` systems is available at
[n8layman/docker-rstudio](https://hub.docker.com/repository/docker/n8layman/rstudio-server/general).
More information on how to start up rocker based containers including
using environment variables to set the container user and the password
is available at
[rocker-project.org](https://rocker-project.org/images/versioned/rstudio.html).
An example docker-compose file is also available in the
[docker/rstudio](docker/rstudio) folder.

## References

#### This project uses [targets](https://books.ropensci.org/targets/) to ensure that the analysis is reproducible.

#### This project uses [gitflow](https://github.com/nvie/gitflow) to manage project development.

#### This project uses [git-crypt](https://github.com/AGWA/git-crypt) to encrypt sensitive information such as API keys.

#### This project used [renv](https://rstudio.github.io/renv/articles/renv.html) to manage the analysis environment and package versions

#### This project uses [rocker-project.org](https://rocker-project.org/images/versioned/rstudio.html) based container images.
