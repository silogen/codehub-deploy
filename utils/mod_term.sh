#!/bin/zsh

sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Set nano as the default text editor
export EDITOR=nano
export VISUAL=$EDITOR

# Configure git to use nano as the default editor
git config --global core.editor "nano"
