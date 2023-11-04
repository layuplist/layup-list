FROM gitpod/workspace-postgresql

RUN sudo install-packages postgresql-12 postgresql-contrib-12
RUN sudo apt-get update \
 && sudo rm -rf /var/lib/apt/lists/*