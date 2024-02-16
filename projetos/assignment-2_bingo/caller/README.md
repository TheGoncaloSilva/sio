# Introduction

The Caller is the game host. It analyzes and controls each player envolved in the game. It also generates the deck, composed by `N` possible numbers.

# Execute it

For the caller to run, you need to first initiate the Playing Area, after that, just execute the following commmand

```
python3 caller.py
```

`Note:` The caller.py program has a set of arguments that can be provided, to see them, execute the python command with the `-h` argument

# Documentation

`Note:` When exchanging messages with the Playing Area, those messages are always made with the indications present on the API listed in the Playing Area `README` file.

## Functioning

The caller operates on a action-reaction module, which means that it executes operations and produces responses based on the messages received. The only exception to this rule is the log in messages. In terms of asymmetric key encryption, the keys used are generated every game and also stored on  the `caller` folder, in `.pem` format.

## Finite-state Machine

### Game state

In order to keep track of the received messages and to not execute unwanted expired commands throughout the game, the caller implements a Finite-state Machine with the states, transitions and meaning represented in the following table:

| State       | Possible Transitions | Meaning                      |
| ----------- | -------------------- | ---------------------------- |
| AUTH        | IDLE                 | Caller log in                |
| IDLE        | SUBMIT_CARD          | Waiting for game start       |
| SUBMIT_CARD | IDLE, SUBMIT_DECK    | Game started, exchange cards |
| SUBMIT_DECK | IDLE, SUBMIT_KEYS    | Exchange shuffled deck       |
| SUBMIT_KEYS | IDLE, EVALUATION     | Exchange symmetric keys      |
| EVALUATION  | IDLE, END_GAME       | Analyze supplied info        |
| END_GAME    | IDLE                 | Game ended, show winner/s    |

### Handling requests

Since the caller may be receiving multiple messages at a given time, another Finite-state Machine and a UUID is used to keep track of requests made to players or playing area. With this, if the caller makes a request, for example, in the log in, it'll include a UUID field in the message and when the Playing Area responds to the request, the UUID will also be in the response message. This detail, coupled to a Finite-state Machine and another variable, allows us to keep track of requests and responses received. The Finite-State Machine is defined as follows:

| State     | Possible Transitions | Meaning                        |
| --------- | -------------------- | ------------------------------ |
| FREE      | REQUESTED            | No requests made               |
| REQUESTED | FREE                 | Request made, waiting response |

## Starting

For starting, the `Caller` class will be created and the caller will connect itself to the Playing Area, remaining in `AUTH` state. Once connected, the caller will request a `nonce` value and send it's public key to the Playing Area (If the caller chose to use card, it will send the certificate instead the public key in this step). When that nonce is received, a awsner will be issued containing all the information about the caller and signed with it's private key (If the caller chose to use card, the message will be signed by the card and a generated public key, for use beyond that point, will also be sent). The Playing area then receives and verifies the authenticity of this message. If everything is correct the caller will be authenticated and pass to the `IDLE` state.

## Connected to playing area

After establishing connection and authentication with the Playing Area, the caller remains in a state waiting to start the game. For the game to start, there needs to be at least two players authenticated and logged in. Once the number of players reaches the maximum number of players supplied by the Playing Area, the game automatically starts with the caller sending a `start_game` message. The caller itselfs transition to the `SUBMIT_CARD` state.

## Disconnection

Before the game starts, there may happen that a player leaves or disconnects from the game, in that case, every entity of the game will remove the player from their records and adjust the player with the seq behind them.

For example, there are 4 players in the game, if the player with seq 2 leaves the game, the players with seq 3 and 4 will subtract `1` to their seq numbers. All entities make this cahnge in their records.

`Note:` This action is only possible before the game starts, after that a player that leaves will be `banned`.

## Exchange Cards

This is the first state of the game. In this state, the players will send their chosen cards, encrypted with their generated Symmetric keys. The caller saves all cards to be decrypted and compared later.

## Exchange Deck

In the second state of the game. After all players submit their cards. The caller will transitions to `SUBMIT_DECK` state. In this state it'll start by sending a message containing the generated encrypted deck. After receiving the caller message, each player, in order, will send their shuffled deck submission, based on the previous shuffle. The caller will register every submission, to be compared later.

## Exchange keys

The third state is probably the most important state. After every player submitted the shuffled deck, the caller will transition to a `SUBMIT_DECK` state. In this states, the caller and the players will submit their Symmetric keys.

## Evaluate winner predictions

After exchangin the Symmetric keys, the caller will proceed to `EVALUATION` state. Here, the caller decrypts the players cards and checks if they contain correct values and then tries to decrypt every shuffled deck in Descending order. It's assumed that the players will do the exact same steps, so that they can also evaluate the winner. In this state, if something doesn't match out, shuffled deck with wrong keys, cards no in the initial deck or the provided player set of cards doesn't contain the correct cards, the players that caused those problems will be issued a ban.

If all went well, the players will submit their predictions for game winners. The caller will save everyone's predictions and calculate his own. Then, the players that made a bad prediction, if there is any, will be banned from the game. If they were part of the the winners, then the caller will calculate new winners. After this, the caller will send the winners to the players.

## Banning

As mentioned above, if a player leaves or disconnects during a game, he will be banned. He will also be banned if he provided a bad set of cards, shuffled the deck in a bad way, sended a message with a bad signature, sent a invalid set of keys or made a bad game prediction.

If a player is banned during a ongoing game the game will end. The only exception is if a player is banned because of a bad winner prediction, because banning him wouldn't affect the state of the game. However, if banning a player means that there is only 1 player left, then the game will automatically end.

`Note:` The bans only apply to the current game and not future games.

## End game

In the last state `END_GAME` the caller will just show the winner and deck. After that he will have the option to get the list of players and logs recorded in the Playing Area. When he is done, he can just exit the match. This will be done through options on screen. During the time that the caller stays in game, the players can also interact in the same way, with the Playing Area. However, when the caller exits the game, the players will also be disconnected.

During this phase, the caller will also be able to request the users lists and audit logs to the Playing Area.

## Cheats

The cheats that the player can reproduced were already descrived above. However, for the caller, since we have trust in the caller procedures, the only cheat that he will be able to produce is message with invalid or no signature.
