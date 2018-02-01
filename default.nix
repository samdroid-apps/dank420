with import <nixpkgs> {};

let
  deps = import ./deps.nix;
in
stdenv.mkDerivation rec {
  name = "env";

  buildInputs = deps.all;

  shellHook =
    ''
        export FISH_P1="(ssg) "
        export FISH_P1_COLOR="yellow"

        ${figlet}/bin/figlet SSG SHELL

        fish; exit
    '';
}
