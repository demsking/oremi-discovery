let
  SERVICE_PORT = "5105";
  DOCKER_USER = "oremi";
  DOCKER_UID = "1000";
  DOCKER_NAMESPACE = "demsking";
  overlay = self: super: {
    oremi-discovery = self.poetry2nix.mkPoetryApplication {
      projectDir = ./.;
      python = self.python310;
      groups = [ ]; # TODO Find how to ignore dev dependencies
      preferWheels = false;
      overrides = self.poetry2nix.defaultPoetryOverrides.extend(self: super: {
        pydantic = super.pkgs.python3Packages.callPackage ./packages/pydantic {};
        oremi-core = super.pkgs.python3Packages.callPackage ./packages/oremi-core {};
        pylint-pydantic = super.pkgs.python3Packages.callPackage ./packages/pylint-pydantic {};
        unqlite = super.unqlite.overridePythonAttrs
        (
          old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ super.setuptools ];
          }
        );
      });
    };
  };
  hostPkgs = import <nixpkgs> { overlays = [ overlay ]; };
  linuxPkgs = import <nixpkgs> { overlays = [ overlay ]; system = "x86_64-linux"; };
  oremi-files = linuxPkgs.runCommand "oremi-files" {} ''
    mkdir -p $out/oremi
    cp ${./LICENSE} $out/oremi/LICENSE
    cp ${./pyproject.toml} $out/oremi/pyproject.toml
  '';
  createDockerUser = linuxPkgs.runCommand "create-docker-user" {} ''
    mkdir -p $out/etc/pam.d
    echo "root:x:0:0::/root:/bin/sh" > $out/etc/passwd
    echo "${DOCKER_USER}:x:${DOCKER_UID}:${DOCKER_UID}::/home/${DOCKER_USER}:" >> $out/etc/passwd
    echo "root:!x:::::::" > $out/etc/shadow
    echo "${DOCKER_USER}:!:::::::" >> $out/etc/shadow

    echo "root:x:0:" > $out/etc/group
    echo "${DOCKER_USER}:x:${DOCKER_UID}:" >> $out/etc/group
    echo "root:x::" > $out/etc/gshadow
    echo "${DOCKER_USER}:!::" >> $out/etc/gshadow
  '';
in
{
  inherit (hostPkgs) oremi-discovery;

  docker = hostPkgs.dockerTools.streamLayeredImage {
    name = "${DOCKER_NAMESPACE}/${linuxPkgs.oremi-discovery.pname}";
    tag = linuxPkgs.oremi-discovery.version;
    contents = [
      createDockerUser
      linuxPkgs.curl
#       linuxPkgs.bashInteractive
#       linuxPkgs.coreutils
      linuxPkgs.oremi-discovery
      oremi-files
    ];
    config = {
      User = DOCKER_USER;
      Env = [];
      WorkingDir = "/oremi";
      ExposedPorts = {
        "${SERVICE_PORT}/tcp" = {};
      };
      Healthcheck = {
        Test = [ "CMD" "curl -f http://localhost:${SERVICE_PORT} || exit 1" ];
      };
      Labels = {
        package-name = linuxPkgs.oremi-discovery.pname;
        package-version = linuxPkgs.oremi-discovery.version;
        maintainer = "Sébastien Demanou <demsking@gmail.com>";
      };
      EntryPoint = [ linuxPkgs.oremi-discovery.pname "--host" "::" "--port" SERVICE_PORT ];
    };
  };
}
