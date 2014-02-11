set -e
set -x
env

echo Installing tty.js

sudo apt-get update
sudo apt-get install git-core curl build-essential openssl libssl-dev -y
git clone https://github.com/joyent/node.git
pushd node
git checkout v0.10.25
./configure
make
sudo make install
popd

node -v


curl https://www.npmjs.org/install.sh > npm_install.sh
sudo sh npm_install.sh

sudo npm -g install tty.js

tty.js --daemonize --port 8080
