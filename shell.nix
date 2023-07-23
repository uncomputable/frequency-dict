{ pkgs ? import <nixpkgs> {}
}:
let
  my-python-packages = python-packages: with python-packages; [
    jaconv
  ];
  my-python = pkgs.python3.withPackages my-python-packages;
in
  pkgs.mkShell {
    buildInputs = [
      my-python
    ];
  }
