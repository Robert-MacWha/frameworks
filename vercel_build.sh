#!/bin/bash
mkdir bin
curl -sSL https://github.com/rust-lang/mdBook/releases/download/v0.4.40/mdbook-v0.4.40-x86_64-unknown-linux-gnu.tar.gz | tar -xz --directory=bin 
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
curl -sSL https://github.com/catppuccin/mdBook/releases/download/v2.2.0/mdbook-catppuccin-x86_64-unknown-linux-gnu.tar.gz |  tar -xz --directory=bin
mv bin/mdbook-catppuccin-x86_64-unknown-linux-gnu/mdbook-catppuccin bin/
curl -sSL https://github.com/tommilligan/mdbook-admonish/releases/download/v1.18.0/mdbook-admonish-v1.18.0-x86_64-unknown-linux-gnu.tar.gz | tar -xz --directory=bin/
chmod +x prebuild.sh
./prebuild.sh
bin/mdbook build -d "book/"
