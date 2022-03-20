'''
Synacor Vault Puzzle Solver - Copyright (c) 2022 atom0s [atom0s@live.com]

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

from collections import deque
from operator import add, sub, mul

grid = [
    mul, 8, sub, 1,
    4, mul, 11, mul,
    add, 4, sub, 18,
    22, sub, 9, mul,
] # yapf: disable


def total(moves):
    '''
    Calculates the total of the given list of move operations.

    @param {list} moves - The list of moves to calculate.
    @return {int} The calculated total.
    '''

    r = moves[0]
    o = add

    for x in range(1, len(moves)):
        if callable(moves[x]):
            o = moves[x]
        else:
            r = o(r, moves[x])

    return r


def path_find(pos_start, pos_end):
    '''
    Finds the shortest path between the two given points, using the DFS algorithm.

    @param {tuple} pos_start - The point in the grid where the path should start.
    @param {tuple} pos_end - The point in the grid where the path should end.
    @return {list|None} The list of commands for the path on success, None otherwise.
    '''

    q = deque([(pos_start, [22], [])])

    while q:
        # Obtain the top entry in the queue..
        pos, moves, cmds = q.popleft()

        # If we are in the end room, see if our movement is a correct solution..
        if pos[0] == pos_end[0] and pos[1] == pos_end[1]:
            if total(moves) != 30:
                continue

            return cmds

        # If we moved back to the start room, the path is invalid..
        if pos[0] == pos_start[0] and pos[1] == pos_start[1] and len(cmds) != 0:
            continue

        # If the orb has become invalid, the path is invalid..
        if len(moves) % 2 == 0:
            t = total(moves)
            if t > 1024 or t < 0:
                continue

        # Try to continue pathing in each direction..
        if pos[0] > 0:
            q.append(((pos[0] - 1, pos[1]), moves + [grid[(pos[0] - 1) * 4 + pos[1]]], cmds + ['north']))
        if pos[0] < 3:
            q.append(((pos[0] + 1, pos[1]), moves + [grid[(pos[0] + 1) * 4 + pos[1]]], cmds + ['south']))
        if pos[1] > 0:
            q.append(((pos[0], pos[1] - 1), moves + [grid[pos[0] * 4 + (pos[1] - 1)]], cmds + ['west']))
        if pos[1] < 3:
            q.append(((pos[0], pos[1] + 1), moves + [grid[pos[0] * 4 + (pos[1] + 1)]], cmds + ['east']))

    return None


def main():
    # Find the shortest path between (3, 0) and (0, 3)..
    path = path_find((3, 0), (0, 3))

    # Output the results..
    if path is None:
        print('[!] Failed to find a path!')
    else:
        print(f'[!] Shortest path found, {len(path)} moves:')
        print('[!] Commands:')

        for c in path:
            print(c)


if __name__ == "__main__":
    main()
