{
  description = "poetry env";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/23.05";
    utils.url = "github:numtide/flake-utils";
  };
  outputs = { utils, nixpkgs, ... }: utils.lib.eachDefaultSystem (system:
  let
    pkgs = import nixpkgs {
      inherit system;
    }; 
    myAppEnv = pkgs.poetry2nix.mkPoetryEnv {
      projectDir = ./.;
    overrides = pkgs.poetry2nix.defaultPoetryOverrides.extend
      (self: super: {
        meson = super.meson.overridePythonAttrs
        (
          old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ super.flit-core ];
          }
        );
        lazy-loader = super.lazy-loader.overridePythonAttrs
        (
          old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ super.flit-core ];
          }
        );
        urllib3 = super.urllib3.overridePythonAttrs
        (
          old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ super.hatchling ];
          }
        );
        h11 = super.h11.overridePythonAttrs
        (
          old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ super.hatchling ];
          }
        );
        pysocks = super.pysocks.overridePythonAttrs
        (
          old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ super.hatchling ];
          }
        );
        sniffio = super.sniffio.overridePythonAttrs
        (
          old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ super.hatchling ];
          }
        );
        attrs = super.attrs.overridePythonAttrs
        (
          old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ super.hatchling super.hatch-fancy-pypi-readme super.hatch-vcs ];
          }
        );
      });
    };
  in {
    devShells.default = myAppEnv.env;
  });
}
