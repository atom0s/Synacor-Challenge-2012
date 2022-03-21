# Notes

Here are some useful bits of information taken from the disassembly of `challenge.bin`.

## Location Related Addresses

  * `099E` - _Ruins puzzle door lock status. (Set to 5 to unlock the door.)_
  * `0A7A` - _`lit lantern` status. (Default value is: `7FFF`, set to `0` and the game thinks you have lit the lantern.)_
  * `0AAC` - _The players current room id. (1)_
  * `0AAD` - _The players current room id. (2)_
  * `0E8E` - _Unknown bit flag used in certain areas._

Important room ids:

  * `090D` - _Foothills (`tablet` item.)_
  * `0935` - _Moss Cavern (`empty lantern` item.)_
  * `0962` - _Twisty Passages (Room before the `can` room. Go `north` to get the flag print.)_
  * `0971` - _Twisty Passages (`can` item.)_
  * `0994` - _Ruins (`red coin` item.)_
  * `0999` - _Ruins (Main puzzle room with the `strange monument`.)_
  * `099F` - _Ruins (`teleporter` item.)_
  * `09A4` - _Ruins (`concave coin` item.)_
  * `09A9` - _Ruins (`corroded coin` item.)_
  * `09AE` - _Ruins (`blue coin` item.)_
  * `09B3` - _Ruins (`shiny coin` item)_
  * `09B8` - _Synacor Headquarters (Default `teleporter` location.) (`business card` and `strange book` items.)_
  * `09C2` - _Beach (Secondary `teleporter` location when teleporter is fixed.)_
  * `09F9` - _Tropical Cave Alcove (`journal` item.)_
  * `0A12` - _Vault Door (Room with the actual `Vault` door.)_
  * `0A3F` - _Vault Antechamber (Starting room of the `Vault` puzzle.) (`orb` item.)_
  * `0A53` - _Vault (`mirror` item.)_
  * `0A58` - _Fumbling around in the darkness (`darkness` area when you have no light.)_
  * `0A62` - _Panicked and lost (Room where you will die to a `Grue` doing any additional move.)_

## Item Addresses

Here are the addresses the game stores the item states within. Each item has its own address. When the value is set to 0, the game considers the item 'picked up' and shows it in the players inventory.

  * `0A6E` - _tablet_
  * `0A72` - _empty lantern_
  * `0A76` - _lantern_
  * `0A7A` - _lit lantern_
  * `0A7E` - _can_
  * `0A82` - _red coin_
  * `0A86` - _corroded coin_
  * `0A8A` - _shiny coin_
  * `0A8E` - _concave coin_
  * `0A92` - _blue coin_
  * `0A96` - _teleporter_
  * `0A9A` - _business card_
  * `0A9E` - _orb_
  * `0AA2` - _mirror_
  * `0AA6` - _strange book_
  * `0AAA` - _journal_

_The game is designed to ensure other conditions are met before allowing further progression from working. For example, if you give yourself the `teleporter` immediately and use it, you will go to the Synacor Headquarters like normal, but the flag given is wrong. The `Ruins` puzzle values must be set before the initial `teleporter` flag is given properly._

Item values are based on their 'state'. In their default state, their value is the room number they are located within.

  - `0` - **State:** `Picked Up` - _The value set when an item is considered `picked up` and in the players inventory._
  - `999` - **State:** `Dropped` - _The value set when the `Ruins` puzzle `coin` items are incorrectly placed and instead are dropped to the floor in the same room._

_**Example:** If you set other items to the `dropped` state, they will be removed from your inventory and instead appear in the `Ruins` puzzle room._

This can be easily tested and proven by moving the `tablet` item at the start of the game to the room south with the following commands:

```
# Observe the tablet items current location..
!peek 0A6E

# Set the tablet to be in the room to the south..
!poke 0A6E 0912

# Go south and see the tablet moved here..
south

# Move the tablet back to the first room..
!poke 0A6E 90D

# Go north and see the tablet moved back..
north
```

## Ruins Puzzle Addresses

When using the various `coin` items, they set a series of addresses to their corrosponding value in the order they are used. 

These are also used to set the `teleporter` into a proper state to give the flag properly.

  * `69DE` - _Coin Slot 1_ [Set to: `9`]
  * `69DF` - _Coin Slot 2_ [Set to: `2`]
  * `69E0` - _Coin Slot 3_ [Set to: `5`]
  * `69E1` - _Coin Slot 4_ [Set to: `7`]
  * `69E2` - _Coin Slot 5_ [Set to: `3`]

Functions related to this puzzle are:

  * `1399` - _Function that handles validating the `coins` are placed in the proper order._
  * `1427` - _Starts the actual math check testing if the `coin` order is correct._
  * `1478` - _Sets the coins to be 'dropped' on the ground in the current room._

## Vault Puzzle Addresses

When completing the `Vault` puzzle, there are a few addresses that are used to setup values used when preparing the `mirror` flag. If these are not set correctly, the `mirror` flag given is wrong.

  * `0F6F` - _Holds the current floor operation value. (0 = Add, 1 = Subtract, 2 = Multiply)_
  * `0F70` - _Holds the current orb weight._
  * `0F71` - _Holds the current movement counter._
  * `0F72` - _Unknown, holds a bit flag value._
  * `0F73` - [Set to: `7A56`]
  * `0F74` - [Set to: `242A`]
  * `0F75` - [Set to: `2968`]

Functions related to this puzzle are:

  * `107A` - _Function._
  * `10B7` - _Function._
  * `11B5` - _Function._
  * `1234` - _Function that resets the `orb` puzzle to defaults._
