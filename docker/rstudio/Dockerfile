FROM rocker/rstudio:latest

# Define build arguments
ARG USER
ARG PASSWORD

RUN install2.r --error --skipinstalled --ncpus -1 \
    targets \
    tarchetypes \
    tidymodels \
    dbarts \
    && rm -rf /tmp/downloaded_packages \
    && strip /usr/local/lib/R/site-library/*/libs/*.so

# Expose port 8787 for RStudio Server
EXPOSE 8787

