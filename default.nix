with import <nixpkgs> {};

let
  py = pkgs.python36;
in
stdenv.mkDerivation rec {
  name = "env";

  buildInputs = with py.pkgs; [
    py
    pytest
    jinja2 

    # For the addons
    sass
  ];

  shellHook =
    ''
        export FISH_P1="(ssg) "
        export FISH_P1_COLOR="yellow"

        ${figlet}/bin/figlet SSG SHELL

        fish; exit
    '';
}
