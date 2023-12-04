# save this as shell.nix
{ pkgs ? import <nixpkgs> {}}:

let
	python-packages = ps: with ps; [
		yt-dlp
	];
in
pkgs.mkShell {
	packages = with pkgs; [ 
		(python311.withPackages python-packages)
		rust-analyzer
		cargo
		rustup
		clang
		pkgconfig
		openssl.dev
		opencv
		ffmpeg
		vlc
	];
	RUSTC_VERSION = "stable";
	shellHook = ''
		export PATH=$PATH:''${CARGO_HOME:-~/.cargo}/bin
		export PATH=$PATH:''${RUSTUP_HOME:-~/.rustup}/toolchains/$RUSTC_VERSION-x86_64-unknown-linux-gnu/bin/
	'';
	LIBCLANG_PATH="${pkgs.llvmPackages.libclang.lib}/lib";
	RUST_BACKTRACE=1;
}

