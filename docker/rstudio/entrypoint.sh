#!/bin/bash

# Check if RSTUDIO_PASSWORD is not set
if [ -z "${RSTUDIO_PASSWORD}" ]; then
  # Generate a random password
  RSTUDIO_PASSWORD=$(openssl rand -base64 12)
  echo "Generated RStudio password: ${RSTUDIO_PASSWORD}"
  
  # Export the generated password so it can be used by RStudio
  export RSTUDIO_PASSWORD
fi

# Set the RStudio Server password
echo "${USERNAME}:${RSTUDIO_PASSWORD}" | chpasswd

# Start RStudio Server
exec /init
