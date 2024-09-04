FROM rocker/rstudio:latest

# Define build arguments
ARG RSTUDIO_USER
ARG RSTUDIO_PASSWORD

# Set environment variables based on the build arguments
ENV USER=${RSTUDIO_USER}
ENV PASSWORD=${RSTUDIO_PASSWORD}

RUN install2.r --error --skipinstalled --ncpus -1 \
    targets \
    tarchetypes \
    tidymodels \
    dbarts \
    && rm -rf /tmp/downloaded_packages \
    && strip /usr/local/lib/R/site-library/*/libs/*.so

# Expose port 8787 for RStudio Server
EXPOSE 8787

