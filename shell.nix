{ pkgs ? import <nixpkgs> {}
}:
let
  python3 = pkgs.python3.withPackages (p: with p; [
    jaconv
  ]);
in
  pkgs.mkShell {
    buildInputs = [
      python3
    ];
  }
