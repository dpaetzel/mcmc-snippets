{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    overlays.url = "github:dpaetzel/overlays";
  };

  outputs = { self, nixpkgs, overlays }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        overlays = [ overlays.pymc4 ];
      };
      python = pkgs.python39;
    in {
      devShell.${system} = pkgs.mkShell {
        buildInputs = with pkgs; with python3Packages; [ numpy pandas pymc4 ];
      };
    };
}
