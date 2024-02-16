# Authors

The masterminds behind this project:

* *Tiago Silvestre*, *103554*, *LECI*
* *Gonçalo Silva*, *103244*, *LECI*
* *Pompeu Costa*, *103294*, *LECI*
* *Samuel Teixeira*, *103325*, *LECI*

# Project description

This project consists on implementing a robust protocol for handling a distributed game. The game we will be implementing is Bingo. The implementation focuses on ca server (caller) that will handle the game supervision, a playing area, charged with riderecting the communication and keeping the logs of every operation and multiple clients. All entities communicate over a networl using `python asyncio` streams/sockets

# Setup

This project has some dependencies that need to be met. For installation, feel free to use a [Python Venv](https://docs.python.org/3/library/venv.html) and execute the following command:

```
pip install -r requirements.txt
```

# Github actions

To implement a Agile methodology and some steps of CI/CD, we decided to implement to Github Actions to improve our workflow. One is for running our tests and building the code and the other is for auto-generating documentation. They can be found in the projects `Actions` tab.

# Tests

To guarantee that our separate modules work independently and combined, even when multiple people are working at the same time and making changes, we decided to implement tests using the [pytest framework](https://docs.pytest.org/en/7.2.x/). This tests can be found at the `tests` directory and can be executed by simply running:

```
pytest
```

# Documentation

Documentation is a special part of any project, so in every package, class and methods we created, we made sure to write good comments and information that can be easily updated, auto-generated and compiled into one easily readable file. For that, we chose the [pdoc3](https://pypi.org/project/pdoc3/) auto documentation tool. With this tool we just needed to write comments in the [google styleguide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) and those comments were then compiled into html files. Once a commit is executed, our github action will auto generate the documentation and upload it to the `docs/assignment-2---bingo-19` folder, where it can be executed via a browser.

* If you wish to manually execute the auto-documentation, execute the following command:
  ```
  pdoc3 --html --force -o ./docs .
  ```
* To open the documentation, go to the folder and execute it with your browser of choice, for example
  ```
  brave-browser index.html
  ```

# Pre requirements

This project uses smart cards in order to sign the messages produced. If you don't have a smart card reader there are two options available

1. Run the project without smart cards
2. Set up a virtual smart card environment

The following toturial is not detailed, if anything wrong happens please access https://sweet.ua.pt/jpbarraca/course/sio-2223/lab-cc/
If you wish to set up a the virtual smart card environment make sure you have the following packages apt and pip packages installed

```
sudo apt install pcscd
sudo apt install python3-pip
sudo apt instlal swig
pip3 install --user pykcs11
sudo apt install opensc-pkcs11
sudo apt install autoconf
sudo apt install automake
sudo apt install build-essential
sudo apt install libpcsclite-dev
sudo apt install python3-crypto
sudo apt install libtool
sudo apt install help2man
pip3 install argparse
pip3 install cryptography
```

Now you should clone a github repository made for emulating smart cards, in a directory of your choise run

```
git clone https://github.com/jpbarraca/vsmartcard.git
cd vsmartcard/virtualsmartcard
autoreconf --verbose --install
./configure --sysconfdir=/etc
make
sudo make install
```

You should stop pcscd and run it on a terminal as root

```
systemctl stop pcscd
sudo pcscd -f -d
```

Generate a virtual PTEID

```
cd vsmartcard/pteid
python3 generate_pteid_card.py
cd ../virtualsmartcard/src/vpicc
cp ../../../pteid/card.json .
./vicc -t PTEID -v
```

# Get-Started

To get-started executing our project, you can simply use our provide script. This script navigates to every folder and starts the program associated. You can run it by executing:

```
bash run_safe.sh 4 16
```

If you want to test the program capabilities to handle cheating by players or caller, you can do so by executing the command:

```
bash run_cheat.sh 4 16
```

The `4` is to indicate the number of players, you can specify other number if you wish. The `16` is used to specify the value N of the card generation.
If you wish to alternatively execute every program manually, then execute the following instructions:

* Playing Area:

  ```
  cd playing_area
  python3 playing_area.py
  ```
* Caller:

  ```
  cd caller
  python3 caller.py
  ```
* Player:

  ```
  cd player
  python3 player.py
  ```

`Note:` Every program has a set of arguments that can be provided. To see which, execute the python command with the `-h` argument

# Logs

There is always a balance that needs to be had between too many information in the console or too litle. So we decided to follow the approach of dividing the information. In every program we used a logger that allows us to dump every information to a lof file and also to filter the information that appears to the user. As you can see, if you have executed the project at least once, in every directory, a `logs` folder will appear. In this folder, you can check the logs by yourself, to view the exchanged information betweem the entities of the game and also their responses and decisions.

We know that if you execute our programs a lot of times, too many files may be created. To assist in that, we created a simple bash script that automatically removes all the log files. You can execute by introducing the following command:

```
bash clear_logs.sh
```
# Cryptography Modules

In our work, we needed to use encryption for all kinds of messages. We have two modules, one for symmetric cryptography called "symmetric.py" and the other called "asymmetric.py" for symmetric cryptography. Both of these have their own test modules.

## Symmetric Module

The symmetric module works with AES. We chose a block cipher because it granted safety in the card shuffling / submission process and also it has high diffusion. It has functions to generate a key, encrypt and decrypt values, as well as getting a key in the format of string or bytes. For encryption, we used CTR
Here's a quick review of the functions:

* generate_key

  This function takes a keySize integer that must represent the number of bytes of the key and then it generates the key. If the size is invalid (not divisible by 16), an exception is raised

* encrypt_values

  This function encrypts a message. We chose the CTR mode because it is very robust and doesn't propagate errors. We create a cipher with the key and then we use it to encrypt the values given as input and then return the encrypted message

* decrypt_values

  The function takes the encrypted message, and decrypts it using the decryptor of the cipher of the given key (that needs to be created). Finally, it returns the original message

* bytes_from_string and string_from_bytes

  Those two basically convert a key from bytes into string format or vice-versa
  

## Asymmetric Module

The asymmetric module has functions to deal with typical asymmetric encryption and to deal with Portuguese Citizen Smartcards. The functions are the following:

* save_key

  This function creates a PEM file to store key, wether it is a Private key or a Public key. If the key input is not a public or private key, it raises a TypeError

* public_key_to_string and public_key_from_string

  These functions are used for converting a public key from string format into RSAPublicKey object or vice-versa

* generate_private_key and generate_public_key

  The first function generates a private key and the second gets the public key from its private key

* encrypt_values and decrypt_values

  These two functions encrypt and decrypt messages using OAEP padding and the SHA256 algorithm, which is a very strong hashing algorithm, since it has no vulnerabilites known

* sign_message and verify_signature

  The first function creates a signature of message for authenticity using a private key and the second one verifies if the signature is valid. The PKCS1v15 padding algorithm was chosen because OAEP gave us errors when used (not supported for verification)

### Portuguese Citizen Card Functions

For handling Portuguese Citizen Card authentication, we have a set of functions that open PyKCS11 sessions to obtain useful tools such as the private key for authentication and its certificate. PyKCS11 is a package that makes us capable of using PKCS11 with Python. PKCS11 is a programming interface to create and manipulate cryptographic tokens, such as smartcards. It serves as a connection for higher level applications to access SmartCard functionalities, so it suits our needs.


# Contributions

The Individual contributions for this project are the following:

* *Gonçalo Silva* - *30%*
* *Tiago Silvestre* - *30%*
* *Pompeu Costa* - *22.5%*
* *Samuel Teixeira* - *17.5%*

# Notes
