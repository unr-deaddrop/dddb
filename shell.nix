{ pkgs ? import <nixpkgs> {} }:
let
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
    });
  };
in myAppEnv.env
