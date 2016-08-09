#!/usr/bin/env bash

vagrant plugin install vagrant-proxyconf
vagrant plugin install vagrant-env

curl -sSL https://get.rvm.io | bash -s -- --ignore-dotfiles
echo "source $HOME/.rvm/scripts/rvm" >> ~/.bash_profile
source $HOME/.rvm/scripts/rvm
rvm install 2.2.3

gem install bundler
bundle install
