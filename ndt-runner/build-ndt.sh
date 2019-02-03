# Get build tools

sudo apt-get update
sudo apt-get install automake subversion -y

# Build Jansson library

cd ~
wget http://www.digip.org/jansson/releases/jansson-2.6.tar.gz
tar -xvf jansson-2.6.tar.gz
cd jansson-2.6/
./configure
make

sudo make install

# Build NDT and I2util

cd ~
svn checkout http://ndt.googlecode.com/svn/trunk/ ndt
cd ndt
svn checkout http://anonsvn.internet2.edu/svn/I2util/trunk/ I2util
./bootstrap
./configure
make
cd src
make web100clt

# Run NDT

# TODO: Add shell command to get the server hostname from mlab-ns instead of hardcoding it
./src/web100clt -n ndt.iupui.mlab3.lga05.measurement-lab.org
