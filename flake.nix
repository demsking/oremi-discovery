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
          SKIP = "insert-license";
          VIRTUAL_ENV_DISABLE_PROMPT = "true";
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
            python310Packages.wheel
            python310Packages.twine
            python310Packages.pylint
            python310Packages.autopep8
            python310Packages.virtualenv

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
            check-jsonschema
            gnumake
            pre-commit
            editorconfig-checker
            python310Packages.pyroma
            python310Packages.pre-commit-hooks
            python310Packages.reorder-python-imports
          ];
          shellHook = ''
            # Python
            export PIP_PREFIX=${envDir}
            export PYTHONUSERBASE=${envDir}
            export PYTHON_SITE_PACKAGES=$PIP_PREFIX/${python310.sitePackages}
            export PYTHONPATH=$(pwd):$PYTHON_SITE_PACKAGES:$PYTHONPATH

            # Disable Dart analytics
            dart --disable-analytics > /dev/null

            # Python
            virtualenv `basename ${envDir}`
            source ${envDir}/bin/activate

            # Install pre-commit hooks
            pre-commit install -f
          '';
        };
      });
}
