/*
 *  Source file of a benchmark program involving sorting of an array
 *  of 10000 random strings of length 8 (including terminating zero).
 *  That sorting is repeated a number of times (default is 20 times),
 *  and each time a different array of random strings is generated.
 *  The number of repetitions can be set via command line.
 *
 *  This file is a part of the project "TCG Continuous Benchmarking".
 *
 *  Copyright (C) 2020  Ahmed Karaman <ahmedkhaledkaraman@gmail.com>
 *  Copyright (C) 2020  Aleksandar Markovic <aleksandar.qemu.devel@gmail.com>
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program. If not, see <https://www.gnu.org/licenses/>.
 *
 */

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>

/* Length of an individual random string (including terminating zero) */
#define RANDOM_STRING_LEN             8
/* Number of elements of the array of random strings */
#define NUMBER_OF_RANDOM_STRINGS      10000

/* Number of repetitions to be performed each with different input */
#define DEFAULT_REPETITION_COUNT      20
#define MIN_REPETITION_COUNT          1
#define MAX_REPETITION_COUNT          1000

/* Structure that keeps an array of random strings to be sorted */
struct StringStruct {
    char chars[RANDOM_STRING_LEN];
};

/* Comparison function passed to qsort() */
int compare_strings(const void *element1, const void *element2)
{
    int result;

    result = strcmp((*((struct StringStruct *)element1)).chars,
                    (*((struct StringStruct *)element2)).chars);

    return (result < 0) ? -1 : ((result == 0) ? 0 : 1);
}

/* Generate a random string of given length and containing only small letters */
static void gen_random_string(char *s, const int len)
{
    static const char letters[] = "abcdefghijklmnopqrstuvwxyz";

    for (size_t i = 0; i < (len - 1); i++) {
        s[i] = letters[rand() % (sizeof(letters) - 1)];
    }

    s[len - 1] = 0;
}

int mock_main(int argc, char *argv[])
{
    struct StringStruct strings_to_be_sorted[NUMBER_OF_RANDOM_STRINGS];
    int32_t repetition_count = DEFAULT_REPETITION_COUNT;
    int32_t option;

    /* Parse command line options */
    while ((option = getopt(argc, argv, "n:")) != -1) {
        if (option == 'n') {
            int32_t user_repetition_count = atoi(optarg);

            /* Check if the value is a string or zero */
            if (user_repetition_count == 0) {
                fprintf(stderr, "Error ... Invalid value for option '-n'.\n");
                exit(EXIT_FAILURE);
            }
            /* Check if the value is a negative number */
            if (user_repetition_count < MIN_REPETITION_COUNT) {
                fprintf(stderr, "Error ... Value for option '-n' cannot be a "
                                "number less than %d.\n", MIN_REPETITION_COUNT);
                exit(EXIT_FAILURE);
            }
            /* Check if the value is too large */
            if (user_repetition_count > MAX_REPETITION_COUNT) {
                fprintf(stderr, "Error ... Value for option '-n' cannot be "
                                "more than %d.\n", MAX_REPETITION_COUNT);
                exit(EXIT_FAILURE);
            }
            repetition_count = user_repetition_count;
        } else {
            exit(EXIT_FAILURE);
        }
    }

    srand(1);

    for (size_t i = 0; i < repetition_count; ++i) {
        /* Generate random strings, and, in turn, sort them */
        for (size_t i = 0; i < NUMBER_OF_RANDOM_STRINGS; ++i) {
            gen_random_string(strings_to_be_sorted[i].chars, RANDOM_STRING_LEN);
        }
        qsort(strings_to_be_sorted, NUMBER_OF_RANDOM_STRINGS,
              sizeof(struct StringStruct), compare_strings);
    }

    /* Control printing */
    printf("CONTROL RESULT:\n");
    for (size_t i = 0; i < 2; ++i) {
        printf(" %s", strings_to_be_sorted[i].chars);
    }
    printf("\n");
}

int global_argc;
char** global_argv;

void mock_help() {
    asm volatile (
        "addi sp, sp, -16\n\t"  // 分配栈空间
        "sd ra, 8(sp)\n\t"      // 保存 ra 寄存器的值到栈上
    );
    mock_main(global_argc, global_argv);
    // printf("mock_help_start\n");
    asm volatile (
        "ld ra, 8(sp)\n\t"       // 从栈上恢复 ra 寄存器的值
        "addi sp, sp, 16\n\t"    // 释放栈空间
        "sjalrr  zero, 0(ra)\n\t"
    );
    // printf("mock_help_end\n");
}

void mock_func() {
    // printf("mock_func_start\n");
    asm volatile (
        "li     t3, 0x7f7f7f7f\n\t"
        "auipc  t1, 0\n\t"
        "li     t2, 46\n\t"
        "sict   t1, t2, t3\n\t"

        "la     t0, mock_help\n\t"
        "ssja   t0, zero, zero\n\t"

        "auipc  t0, 0\n\t"
        "li     t1, 22\n\t"
        "ssra   t0, t1, zero\n\t"

        "la     t3, mock_help\n\t"
        "sjalrj  ra, 0(t3)\n\t"
        "sict   zero, zero, zero\n\t"

        "ld ra, 8(sp)\n\t"       // 从栈上恢复 ra 寄存器的值
        "addi sp, sp, 16\n\t"    // 释放栈空间
    );
    // printf("mock_func_end\n");
}

int main(int argc, char* argv[]) {
    global_argc = argc;
    global_argv = argv;
    mock_func();
    return 0;
}