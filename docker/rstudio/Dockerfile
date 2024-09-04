FROM rocker/rstudio:latest

# Update system and install system dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
      libglpk-dev \\
      libcurl4-openssl-dev && \
    rm -rf /var/lib/apt/lists/* 
      
# Install additional R packages
RUN install2.r --error --skipinstalled --ncpus -1 \ 
    curl \
    targets \
    tarchetypes \
    tidymodels \
    dbarts \
    && rm -rf /tmp/downloaded_packages \
    && strip /usr/local/lib/R/site-library/*/libs/*.so

# Expose port 8787 for RStudio Server
EXPOSE 8787

