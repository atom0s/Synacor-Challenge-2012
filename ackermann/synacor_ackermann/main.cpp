/**
 * Synacor Teleporter Solver - Copyright (c) 2022 atom0s [atom0s@live.com]
 *
 * This work is licensed under the Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License.
 * To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-nd/4.0/ or send a letter to
 * Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
 *
 * By using this software, you agree to the above license and its terms.
 *
 *     Attribution - You must give appropriate credit, provide a link to the license and indicate if changes were
 *                 made. You must do so in any reasonable manner, but not in any way that suggests the licensor
 *                 endorses you or your use.
 *
 * Non-Commercial - You may not use the material for commercial purposes.
 *
 * No-Derivatives - If you remix, transform, or build upon the material, you may not distribute the
 *                 modified material. You are, however, allowed to submit the modified works back to the original
 *                 project in attempt to have it added to the original project.
 *
 * You may not apply legal terms or technological measures that legally restrict others
 * from doing anything the license permits.
 *
 * No warranties are given.
 */

/**
 * Modified Ackermann Function
 *
 * The Synacor challenge makes use of a modified version of the Ackermann function. You can read more
 * about the general Ackermann function here:
 * https://en.wikipedia.org/wiki/Ackermann_function
 * https://mathworld.wolfram.com/AckermannFunction.html
 * http://www.mrob.com/pub/math/ln-2deep.html
 * 
 * By default, Ackermann states that:
 * 
 *                  | n + 1                     when m == 0
 *      A(m, n) =   | A(m -1, 1)                when m > 0, n == 0
 *                  | A(m -1, A(m, n - 1)       when m > 0, n > 0
 * 
 * However, with the Synacor variant, the third parameter is introduced and replaces the default
 * usage of 1 in such cases as the second above.
 * 
 *                  | n + 1                     when m == 0
 *   A(m, n, p) =   | A(m - 1, p)               when m > 0, n == 0
 *                  | A(m - 1, A(m, n - 1)      when m > 0, n > 0
 * 
 * We can also make use of the architecture documentation and the initial setup for when this function
 * is called to determine some constraints we can adhere to:
 * 
 *      1. The architecture states the entire system is implemented with int16_t numbers. (15-bit space, modulo 32768)
 *      2. The architecture states the maximum valid number value is '32767'. (Higher is used for registers or is invalid.)
 *      3. The Ackermann function is invoked with: 4, 1, reg[7] as the arguments.
 * 
 * From this, we can assume the following:
 * 
 *      1. 'm' can never be higher than 4.
 *      2. 'n' can never be higher than 32767.
 *      3. 'p' can never be higher than 32767.
 * 
 * With this information we can also optimize the Ackermann method by introducing caching via memoization. Since we know the upper
 * bounds of both 'm' and 'n', we know that the maximum available condition to occur is '5 * 32768'. We can optimize this further
 * as well by turning the cache into a single-dimension array and using the input and bounds as a lookup key. (n * 5 + m)
 * 
 * Further optimizations can be made by implementing the information from the Wikipedia article and other papers regarding the
 * Ackermann function to help reduce the number of recursive calls. For now, 'm' cases where it equals 0, 1, and 2 are handled.
 * 
 * As-is, this can produce a result within a few seconds; plenty fast for me and this challenge.
 */

#include <cinttypes>
#include <cstring>
#include <stdio.h>

/**
 * Stack Size Extension
 *
 * By default, the stack size is set to 1MB. This is not enough space for the Ackermann function
 * to complete its iterations. This linker flag will extend the stack to 8MB instead.
 */

#pragma comment(linker, "/STACK:8388608")

/**
 * Memoization Cache
 * 
 * Single-dimension array to be used as a lookup cache (memoization) with the Ackermann recursion
 * function, allowing for better performance.
 */

#define MEMOIZATION_CACHE_ENABLED 1

#if defined(MEMOIZATION_CACHE_ENABLED) && (MEMOIZATION_CACHE_ENABLED == 1)
constexpr int32_t CACHE_SIZE = 5 * 32768;

int16_t g_Cache[CACHE_SIZE]{};
#endif

/**
 * Synacor customized Ackermann recursion function.
 *
 * @param {int16_t} m - The first value. (Default is 4.)
 * @param {int16_t} n - The second value. (Default is 1.)
 * @param {int16_t} p - The key value. (Value taken from reg[7] in the VM.)
 * @return {int16_t} The computed result.
 */
int16_t ack(int16_t m, int16_t n, int16_t p)
{
    const auto index = n * 5 + m;

#if defined(MEMOIZATION_CACHE_ENABLED) && (MEMOIZATION_CACHE_ENABLED == 1)
    const auto cache = g_Cache[index];

    if (cache != -1)
        return cache;
#endif

    int16_t res = 0;

    if (m == 0)
        res = (n + 1) % 32768;
    else if (m == 1)
        res = (n + p + 1) % 32768;
    else if (m == 2)
        res = ((n + 2) * p + (n + 1)) % 32768;
    else if (n == 0)
        res = ack(m - 1, p, p);
    else
        res = ack(m - 1, ack(m, n - 1, p), p);

#if defined(MEMOIZATION_CACHE_ENABLED) && (MEMOIZATION_CACHE_ENABLED == 1)
    g_Cache[index] = res;
#endif

    return res;
}

/**
 * Application entry point.
 * 
 * @param {int32_t} argc - The argument count passed to the application.
 * @param {char*[]} argv - The array of arguments.
 * @return {int32_t} 0 on success, 1 otherwise.
 */
int32_t __cdecl main(int32_t argc, char* argv[])
{
    for (uint32_t x = 0; x < 32768; x++)
    {
#if defined(MEMOIZATION_CACHE_ENABLED) && (MEMOIZATION_CACHE_ENABLED == 1)
        std::memset(&g_Cache, -1, sizeof(int16_t) * CACHE_SIZE);
#endif

        if (ack(4, 1, x) == 6)
        {
            printf_s("[!] Solution found; reg[7] == %d\n", x);
            return 0;
        }
    }

    printf_s("[!] No solution found.\n");
    return 1;
}