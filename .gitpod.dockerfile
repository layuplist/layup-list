FROM gitpod/workspace-postgresql

RUN sudo apt-get update \
 && sudo rm -rf /var/lib/apt/lists/*