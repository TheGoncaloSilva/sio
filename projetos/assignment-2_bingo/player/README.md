# Execute it

For the player to run, you need to first initiate the Playing Area and then the Caller, after that, just execute the following commmand

```
python3 player.py
```

`Note:` The player.py program has a set of arguments that can be provided, to see them, execute the python command with the `-h` argument

# Documentation

`Note:` When exchanging messages with the Playing Area, those messages are always made with the indications present on the API listed in the Playing Area `README` file.

## Functioning

The player operates on a action-reaction module, which means that it executes operations and produces responses based on the messages received. The only exception to this rule is the log in messages. In terms of asymmetric key encryption, the keys used are generated every game and never saved.

## Starting

* Authentication with card:

  * For starting, the player will send the public key and ask for a nonce. Upon receiving the response from the Playing Area, the player signs that message with the private key and sends it back, binding that public key with himself. After that the login process ends.
* Authentication with card:

  * The player will send the certificate and ask for a nonce. Upon receiving the response from the Playing Area, the player signs that message with the card and includes a new public key that will be used beyond that point. It then sents it back, binding that public key with himself. After that the login process ends.

## Disconnection

Before the game starts, there may happen that a player leaves or disconnects from the game, in that case, every entity of the game will remove the player from their records and adjust the player with the seq behind them.

For example, there are 4 players in the game, if the player with seq 2 leaves the game, the players with seq 3 and 4 will subtract `1` to their seq numbers. All entities make this cahnge in their records.

`Note:` This action is only possible before the game starts, after that a player that leaves will be `banned`.

## Exchange Cards

Upon receiving a `game_started` message from the PA, the players create their cards, encrypt them with their generated symmetric key and submit. After every player submits their cards, the game transitions to `SUBMIT_DECK`.

## Exchange Deck

In this state the player listens to every call made until it receives the call from the player before it (ex: player4 waits until receiving the call from player3). When that happens the player will shuffle the deck, encrypt it and submit it.

## Exchange keys

The third state is probably the most important state. After every player submitted the shuffled deck, everyone will start sending the symmetric keys used to everyone else, caller included.

## Evaluate winner predictions

After exchangin the Symmetric keys, the caller will proceed to `EVALUATION` state. Here, the player decrypts the players cards and then tries to decrypt every shuffled deck in Descending order.
After that the player will submit their prediction for game winners and wait for the caller response.

## End game

In the last state `END_GAME` the player will just show the winner and deck.
During this phase, the player will also be able to request the users lists and audit logs to the Playing Area.

## Cheats

The cheats that the player can reproduced are:

    Bad signature
    Card with numbers up to N*2
    Card with more than M elements
    Deck starting with the player card and then filled with random numbers
    Wrong winner. Says he, the player, is the winner
