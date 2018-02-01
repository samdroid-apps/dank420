with import <nixpkgs> {};

let
  deps = import ./deps.nix;
  py = deps.py;
in
  py.pkgs.buildPythonPackage rec {
    pname = "dank420";
    version = "0.1";
    name = "${pname}-${version}";

    src = ./.;

    nativeBuildInputs = deps.forCheck;
    propagatedBuildInputs = deps.forPackage;

    doCheck = true;
    checkPhase = ''pytest'';
  }
