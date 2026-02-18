# Docker Deployment Guide for Santa AI

This guide explains how to build the Docker image, run it locally, and deploy it to a cloud environment.

## 1. Prerequisites

- **Docker Installed**: Ensure Docker Desktop (Windows/Mac) or Docker Engine (Linux) is installed and running.
- **Cloud Account**: Access to a cloud provider like AWS, Google Cloud, Azure, or DigitalOcean.
- **Docker Registry Account** (Optional but recommended): Docker Hub, AWS ECR, etc.

## 2. Build the Docker Image

Open your terminal in the project root directory (where `Dockerfile` is located) and run:

```bash
# Build the image and tag it as 'santa-ai'
docker build -t santa-ai .
```

## 3. Run the Container Locally

To test the application locally:

1.  **Create a `.env` file**:
    Copy the example environment file and adjust values if needed.
    ```bash
    cp .env.example .env
    ```

2.  **Run the container**:
    ```bash
    docker run -d -p 8000:8000 --env-file .env --name santa-ai-container santa-ai
    ```
    - `-d`: Run in detached mode (background).
    - `-p 8000:8000`: Map port 8000 of the container to port 8000 on your machine.
    - `--env-file .env`: Pass environment variables from the file.
    - `--name santa-ai-container`: Give the container a name.

3.  **Verify it's running**:
    ```bash
    docker ps
    ```
    You should see `santa-ai-container` in the list.

4.  **Check logs**:
    ```bash
    docker logs -f santa-ai-container
    ```

5.  **Stop the container**:
    ```bash
    docker stop santa-ai-container
    docker rm santa-ai-container
    ```

## 4. Deploy to Cloud (General "Docker on VM" Approach)

This approach assumes you are using a cloud Virtual Machine (VM) like AWS EC2, DigitalOcean Droplet, or Google Compute Engine.

### Step 4.1: Push Image to a Registry (Recommended)

Instead of building code on the server, it's better to build locally and push the image to a registry.

1.  **Login to Docker Hub** (or your cloud registry):
    ```bash
    docker login
    ```

2.  **Tag your image**:
    Replace `your-username` with your Docker Hub username.
    ```bash
    docker tag santa-ai your-username/santa-ai:latest
    ```

3.  **Push the image**:
    ```bash
    docker push your-username/santa-ai:latest
    ```

### Step 4.2: Deploy on Cloud Server

1.  **SSH into your Cloud Server**.

2.  **Install Docker** on the server (if not already installed).
    *   *Ubuntu example:* `sudo apt-get update && sudo apt-get install docker.io -y`

3.  **Pull and Run**:
    ```bash
    # Pull the image
    sudo docker pull your-username/santa-ai:latest

    # Run the container (ensure port 8000 is open in your server's firewall/security group)
    sudo docker run -d -p 8000:8000 \
      --env-file .env \
      --name santa-ai-app \
      your-username/santa-ai:latest
    ```
    *(Note: You'll need to create a `.env` file on the server or pass environment variables with `-e KEY=VALUE`)*

### Alternative: Build on Server (Simpler for testing)

If you don't want to use a registry yet:

1.  **Copy your code** to the server (using git clone or scp).
2.  **Run the build command** on the server:
    ```bash
    docker build -t santa-ai .
    ```
3.  **Run the container** as shown in Step 3.

## 5. Free Cloud Deployment Options

Here are two popular platforms with free tiers that make deploying Docker containers easy.

### Option A: Render (Easiest)

Render is great because it can build your Dockerfile directly from GitHub without needing a registry.

1.  **Push your code to GitHub**.
2.  **Sign up** at [render.com](https://render.com).
3.  Click **"New +"** -> **"Web Service"**.
4.  Connect your **GitHub repository**.
5.  **Configure**:
    - **Name**: `santa-ai`
    - **Runtime**: Select **Docker**.
    - **Instance Type**: Select **Free**.
    - **Environment Variables**: Add your `.env` variables (except `PORT`, Render sets that automatically).
6.  Click **Create Web Service**.

*Note: The free tier spins down after 15 minutes of inactivity. The first request after that will take about 30 seconds to load.*

### Option B: Fly.io (Performance)

Fly.io runs your container on a micro-VM near you.

1.  **Install flyctl**:
    - **Windows (PowerShell)**: `iwr https://fly.io/install.ps1 -useb | iex`
    - **Mac/Linux**: `curl -L https://fly.io/install.sh | sh`
2.  **Login**:
    ```bash
    fly auth login
    ```
3.  **Launch**:
    Run this in your project folder:
    ```bash
    fly launch
    ```
    - It will detect the Dockerfile.
    - Follow the prompts to set a name and region.
    - It will generate a `fly.toml` file.
4.  **Deploy**:
    ```bash
    fly deploy
    ```

*Note: You may need to add a credit card for identity verification, even for the free tier.*

## 6. Automating with GitHub Actions

We have added a workflow file at `.github/workflows/docker-publish.yml`. This automatically builds and pushes your Docker image to Docker Hub whenever you push to the `main` branch.

### Setup Required:

1.  Go to your GitHub Repository.
2.  Click **Settings** -> **Secrets and variables** -> **Actions**.
3.  Click **New repository secret**.
4.  Add the following secrets:
    - `DOCKER_USERNAME`: Your Docker Hub username.
    - `DOCKER_PASSWORD`: Your Docker Hub access token (from Account Settings -> Security -> Access Tokens).

Once set, every push to `main` will update your image on Docker Hub!

