FROM rocker/rstudio:latest

# Define build arguments
ARG USERNAME=rstudio
ARG RSTUDIO_PASSWORD

# Set environment variables based on the build arguments
ENV USERNAME=${USERNAME}
ENV PASSWORD=${RSTUDIO_PASSWORD}

# Create the user and set the home directory
RUN useradd -m ${USERNAME}

# Set the working directory to a subdirectory within the user's home directory
# WORKDIR /home/${USERNAME}/projects

# Switch to the new user
# USER ${USERNAME}

# Expose port 8787 for RStudio Server
EXPOSE 8787

