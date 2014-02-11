set -e
set -x

pwd

env

echo < /dev/tty

echo Installing tty.js

sudo apt-get update
sudo apt-get install git-core curl build-essential openssl libssl-dev -y
cd /tmp/

# Node
git clone https://github.com/joyent/node.git
pushd node
git checkout v0.10.25
./configure
make
sudo make install
popd

node -v

# Npm
git clone git://github.com/isaacs/npm.git
pushd npm
sudo make install
popd

npm -v

# tty.js
sudo npm -g install tty.js

tty.js --daemonize --port 8080
