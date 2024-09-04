FROM rocker/rstudio:latest

# Define build arguments
ARG USERNAME=rstudio
ARG RSTUDIO_PASSWORD

# Set environment variables based on the build arguments
ENV USERNAME=${USERNAME}
ENV RSTUDIO_PASSWORD=${RSTUDIO_PASSWORD}

# Create the user and set the home directory
RUN useradd -m ${USERNAME}

# Set the working directory to a subdirectory within the user's home directory
WORKDIR /home/${USERNAME}/projects

# Switch to the new user
USER ${USERNAME}

# Expose port 8787 for RStudio Server
EXPOSE 8787

# Add the entrypoint script
COPY ./entrypoint.sh /usr/local/bin/entrypoint.sh

# Make the script executable
RUN chmod +x /usr/local/bin/entrypoint.sh

# Use the custom entrypoint script
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
