with import <nixpkgs> {};

let
  py = pkgs.python36;
  python-frontmatter = py.pkgs.buildPythonPackage rec {
    pname = "python-frontmatter";
    version = "0.4.2";
    name = "${pname}-${version}";

    propagatedBuildInputs = with py.pkgs; [ six pyyaml ];

    # Seems to require terminal
    #    ValueError: underlying buffer has been detached
    doCheck = false;

    src = py.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "1hbrgyh324s0cg913f0pqzs6l4f2hzvmqsf16z4qxl4p06nlkbma";
    };
  };
  lookupy = py.pkgs.buildPythonPackage rec {
    pname = "Lookupy";
    version = "0.2";
    name = "${pname}-${version}";

    nativeBuildInputs = with py.pkgs; [ nose ];

    src = py.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "184h79zsrlrwak8y0sl2vkz9yik695zqx6633i7x0r56pra6sh04";
    };
  };
in
stdenv.mkDerivation rec {
  name = "env";

  buildInputs = with py.pkgs; [
    py
    pytest
    jinja2 
    lookupy
    watchdog

    # For the addons
    sass
    python-frontmatter
  ];

  shellHook =
    ''
        export FISH_P1="(ssg) "
        export FISH_P1_COLOR="yellow"

        ${figlet}/bin/figlet SSG SHELL

        fish; exit
    '';
}
