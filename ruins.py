'''
Synacor Ruins Puzzle Brute-Forcer - Copyright (c) 2022 atom0s [atom0s@live.com]

This work is licensed under the Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-nd/4.0/ or send a letter to
Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

By using this software, you agree to the above license and its terms.

    Attribution - You must give appropriate credit, provide a link to the license and indicate if changes were
                made. You must do so in any reasonable manner, but not in any way that suggests the licensor
                endorses you or your use.

Non-Commercial - You may not use the material for commercial purposes.

No-Derivatives - If you remix, transform, or build upon the material, you may not distribute the
                modified material. You are, however, allowed to submit the modified works back to the original
                project in attempt to have it added to the original project.

You may not apply legal terms or technological measures that legally restrict others
from doing anything the license permits.

No warranties are given.
'''

from random import shuffle


def get_coin(n):
    '''
    Returns the name of the coin of the given number.

    @param {int} n - The number of the coin.
    @return {string} The name of the coin.
    '''

    return {2: 'red', 3: 'corroded', 5: 'shiny', 7: 'concave', 9: 'blue'}[n]


def main():
    while True:
        # Randomize the order of the current values..
        v = [2, 3, 5, 7, 9]
        shuffle(v)

        # Attempt to solve the problem..
        r = v[0] + v[1] * v[2] ** 2 + v[3] ** 3 - v[4]

        if r == 399:
            coins = list(map(lambda x: get_coin(x), v))
            print(f'[!] Solution: {coins}')
            print('[!] Commands:')

            for c in coins:
                print(f'use {c} coin')

            break


if __name__ == "__main__":
    main()
