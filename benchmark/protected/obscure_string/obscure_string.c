/*
 *  Source file of a benchmark program involving obscuring a set of
 *  random strings of a constant length by xoring them with 42.
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

#define MAX_STRING_LENGHT              15
#define NUMBER_OF_RANDOM_STRINGS       100
#define DEFAULT_NUMBER_OF_REPETITIONS  30000
#define MAX_NUMBER_OF_REPETITIONS      1000000000
#define NUMBER_OF_CONTROL_PRINT_ITEMS  5

/* Structure for keeping an array of strings */
struct StringStruct {
    char chars[MAX_STRING_LENGHT + 1];
};

/**
 * Sets characters of the given string to random small letters a-z.
 * @param s String to get random characters.
 * @len Length of the input string.
 */
static void gen_random_string(char *chars, const int len)
{
    static const char letters[] = "abcdefghijklmnopqrstuvwxyz";

    for (size_t i = 0; i < len; i++) {
        chars[i] = letters[rand() % (sizeof(letters) - 1)];
    }
    chars[len] = 0;
}

void mock_main (int argc, char* argv[])
{
    struct StringStruct random_strings[NUMBER_OF_RANDOM_STRINGS];
    struct StringStruct strings_to_be_obscured[NUMBER_OF_RANDOM_STRINGS];
    int32_t number_of_repetitions = DEFAULT_NUMBER_OF_REPETITIONS;
    int32_t option;

    /* Parse command line options */
    while ((option = getopt(argc, argv, "n:")) != -1) {
        if (option == 'n') {
            int32_t user_number_of_repetitions = atoi(optarg);
            /* Check if the value is a negative number */
            if (user_number_of_repetitions < 1) {
                fprintf(stderr, "Error ... Value for option '-n' cannot be a "
                                "negative number.\n");
                exit(EXIT_FAILURE);
            }
            /* Check if the value is a string or zero */
            if (user_number_of_repetitions == 0) {
                fprintf(stderr, "Error ... Invalid value for option '-n'.\n");
                exit(EXIT_FAILURE);
            }
            /* Check if the value is too large */
            if (user_number_of_repetitions > MAX_NUMBER_OF_REPETITIONS) {
                fprintf(stderr, "Error ... Value for option '-n' cannot be "
                                "more than %d.\n", MAX_NUMBER_OF_REPETITIONS);
                exit(EXIT_FAILURE);
            }
            number_of_repetitions = user_number_of_repetitions;
        } else {
            exit(EXIT_FAILURE);
        }
    }

    /* Create an array of strings with random content */
    srand(1);
    for (size_t i = 0; i < NUMBER_OF_RANDOM_STRINGS; i++) {
        gen_random_string(random_strings[i].chars, MAX_STRING_LENGHT);
    }

    /* Perform uppercasing of a set of random strings multiple times */
    for (size_t j = 0; j < number_of_repetitions; j++) {
        /* Copy initial set of random strings to the set to be obscured */
        memcpy(strings_to_be_obscured, random_strings,
               NUMBER_OF_RANDOM_STRINGS * (MAX_STRING_LENGHT + 1));
        /* Do actual changing case to uppercase */
        for (size_t i = 0; i < NUMBER_OF_RANDOM_STRINGS; i++) {
            int k = 0;
  
            while (strings_to_be_obscured[i].chars[k]) { 
                char ch = strings_to_be_obscured[i].chars[k] ^ 42; 
                memcpy((void *)strings_to_be_obscured[i].chars + k,
                       &ch, 1);
                k++; 
            } 
        }
    }

    /* Control printing */
    printf("CONTROL RESULT: (obscure_string)\n");
    for (size_t i = 0; i < NUMBER_OF_CONTROL_PRINT_ITEMS; i++) {
        printf(" %s", random_strings[i].chars);
    }
    printf("\n");
    for (size_t i = 0; i < NUMBER_OF_CONTROL_PRINT_ITEMS; i++) {
        printf(" %s", strings_to_be_obscured[i].chars);
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