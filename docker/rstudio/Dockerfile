FROM rocker/rstudio:latest

# Define build arguments
ARG RSTUDIO_USERNAME
ARG RSTUDIO_PASSWORD

# Set environment variables based on the build arguments
ENV USER=${USERNAME}
ENV PASSWORD=${RSTUDIO_PASSWORD}

# Expose port 8787 for RStudio Server
EXPOSE 8787

