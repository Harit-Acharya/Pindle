#!/bin/bash

gnome-terminal --window --full-screen

echo "Installing ............. PINDLE"
echo "To install PINDLE on your device enter root password:"
sudo su -l

cd /home
PATH="/home/YourDrive"

if [[ -e YourDrive]];
    then
    echo "Transferring YourDrive data into User_YourDrive........"
    mkdir User_YourDrive
    mv YourDrive/* User_YourDrive
    rmdir YourDrive
fi

mkdir $PATH
cd $PATH
mkdir $PATH/Documents
mkdir $PATH/Pictures
mkdir $PATH/Music
mkdir $PATH/Videos

cd ~
ln -s $PATH YourDrive

mv ~/Documents/* $PATH/Documents
mv ~/Music/* $PATH/Music
mv ~/Pictures/* $PATH/Pictures
mv ~/Videos/* $PATH/Videos

chmod a=r ~/Documents
chmod a=r ~/Music
chmod a=r ~/Pictures
chmod a=r ~/Videos

chmod +x findandsort.sh
./findsort.sh

