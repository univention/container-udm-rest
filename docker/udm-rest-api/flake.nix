{
  description = "Experimental packaging of dependencies as a Nix Flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";

    # NOTE: Specifying the source repository as a Flake input will put it into
    # the lock file "flake.lock" and handle updates via "nix flake update". An
    # alternative would be to use "fetchGitlab" in the "src" attributes and have
    # the version pinning in there.
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
            # NOTE: The web assets are not really built, copying the wanted
            # files into the output directory is enough to package it.
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
