{
  lib,
  callPackage,
  poetry2nix,
  buildPythonPackage,
  fetchFromGitLab,
  python310,
}:
let
  version = "1.0.0.dev13";
in
poetry2nix.mkPoetryApplication {
  projectDir = fetchFromGitLab{
    owner = "demsking";
    repo = "oremi-core";
    rev = "v${version}";
    hash = "sha256-EIpKoiuG2K3aYyYgkz0b1Rm65VmpQPsuDy3pmURSWBE=";
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
