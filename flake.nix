{
  description = "Oremi Discovery";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/23.05";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        envDir = "./venv";
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShell = with pkgs; mkShell rec {
          EDITOR = "vim";
          PYTHONPATH = ".:./clients/python:$PYTHONPATH";
          buildInputs = [
            # tmux
            git
            tmux
            gitmux
            tmuxinator

            # devtools
            dart
            poetry
            python310
            python310Packages.pip
            python310Packages.wheel
            python310Packages.twine
            python310Packages.pylint
            python310Packages.virtualenv
            python310Packages.toml

            # tests
            python310Packages.pytest-mock
            python310Packages.pytest
            python310Packages.pytest-cov
            python310Packages.pluggy
            python310Packages.pytest-asyncio
            nodePackages.nodemon

            # certificates
            openssl

            # pre-commit
            ruff
            which
            nodejs
            hadolint
            check-jsonschema
            gnutar
            gnumake
            bandit
            skjold
            shellcheck
            prospector
            pre-commit
            editorconfig-checker
            python310Packages.doc8
            python310Packages.pyroma
            python310Packages.pre-commit-hooks
            python310Packages.reorder-python-imports
          ];
          shellHook = ''
            export SERVICE_HOST="$(hostname -I | awk '{print $1}')"

            # Disable Dart analytics
            dart --disable-analytics > /dev/null

            # Python
            virtualenv `basename ${envDir}`
            VIRTUAL_ENV_DISABLE_PROMPT=true source ${envDir}/bin/activate

            # Node.js
            mkdir -p .nix-node
            export NODE_PATH=$PWD/.nix-node
            export PATH=$NODE_PATH/bin:$PATH
            npm config set prefix $NODE_PATH

            if ! which gimtoc &> /dev/null; then
              npm install -g gimtoc
            fi

            # Install pre-commit hooks
            pre-commit install -f
          '';
        };
      });
}
