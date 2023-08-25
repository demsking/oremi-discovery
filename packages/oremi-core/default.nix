{
  lib,
  callPackage,
  poetry2nix,
  buildPythonPackage,
  fetchFromGitLab,
  python310,
}:
let
  version = "1.0.0.dev15";
in
poetry2nix.mkPoetryApplication {
  projectDir = fetchFromGitLab{
    owner = "demsking";
    repo = "oremi-core";
    rev = "v${version}";
    hash = "sha256-HVGukC1mk/4dHFOKCEEb9kpRwMQBIiYiJcGc4o/xdfY=";
  };
  python = python310;
  groups = [ ]; # TODO Find how to ignore dev dependencies
  preferWheels = false;
  overrides = poetry2nix.defaultPoetryOverrides.extend(self: super: {
    pydantic = callPackage ../pydantic {};
    unqlite = super.unqlite.overridePythonAttrs (
      old: {
        buildInputs = (old.buildInputs or [ ]) ++ [ super.setuptools ];
      }
    );
  });
}
