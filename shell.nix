{ pkgs ? import (builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/4ecab3273592f27479a583fb6d975d4aba3486fe.tar.gz";
    sha256 = "10wn0l08j9lgqcw8177nh2ljrnxdrpri7bp0g7nvrsn9rkawvlbf";
  }) {}
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
