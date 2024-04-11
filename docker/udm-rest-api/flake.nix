{
  description = "Experimental packaging of dependencies";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";

    ucs-sources = {
      type = "gitlab";
      owner = "univention";
      repo = "ucs";
      ref = "5.0-6";
      host = "git.knut.univention.de";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, flake-utils, ucs-sources }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        stdenv = pkgs.stdenv;
      in {
        packages = rec {
          udm-rest-web-assets = stdenv.mkDerivation {
            pname = "udm-rest-web-assets";
            version = "0.0.1";
            src = ucs-sources;
            dontUnpack = true;
            dontBuild = true;
            installPhase = ''
              mkdir -p $out
              cp -av $src/management/univention-directory-manager-rest/var $out
            '';
          };
        };
      }
    );
}
