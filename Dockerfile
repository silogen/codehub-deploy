FROM python:3.9.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y apt-utils && \
    DEBIAN_FRONTEND=noninteractive apt-get install --fix-missing -y \
    curl \
    apt-transport-https \
    gnupg \
    unzip \
    lsb-release \
    git \
    zsh \
    mc \
    nano \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install OpenTofu
RUN curl --proto '=https' --tlsv1.2 -fsSL https://get.opentofu.org/install-opentofu.sh -o install-opentofu.sh && \
    chmod +x install-opentofu.sh && \
    ./install-opentofu.sh --install-method deb && \
    rm -f install-opentofu.sh

# Install kubectl from official source
RUN curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.32/deb/Release.key | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg && \
    chmod 644 /etc/apt/keyrings/kubernetes-apt-keyring.gpg && \
    echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.32/deb/ /' | tee /etc/apt/sources.list.d/kubernetes.list && \
    chmod 644 /etc/apt/sources.list.d/kubernetes.list  && \
    apt-get update && apt-get install -y kubectl && \
    rm -rf /var/lib/apt/lists/*

# Install Helm using binary download
RUN curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | tee /usr/share/keyrings/helm.gpg > /dev/null && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | tee /etc/apt/sources.list.d/helm-stable-debian.list && \
    apt-get update && apt-get install -y helm && \
    rm -rf /var/lib/apt/lists/*

# Install Google Cloud CLI and gke-gcloud-auth-plugin
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update && apt-get install -y \
    google-cloud-sdk \
    google-cloud-sdk-gke-gcloud-auth-plugin\
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy requirements
COPY dev_requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r dev_requirements.txt

# Copy the rest of the application
COPY . .
RUN pip install -e .

# Create directories for mounted volumes
RUN mkdir -p /app/deployments /app/secrets /app/codehub /app/utils

# Set up zsh as default shell
RUN chsh -s /bin/zsh root && utils/mod_term.sh

# Set default command
CMD ["/bin/zsh"]

# Volume configuration
VOLUME ["/app/deployments", "/app/secrets"]
