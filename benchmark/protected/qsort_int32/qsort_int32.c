/*
 *  Source file of a benchmark program involving sorting of an array
 *  of length n whose elements are "int32_t". The default value for n
 *  is 300000, and it can be set via command line as well.
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

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

/* Number of elements in the array to be sorted */
#define DEFAULT_ARRAY_LEN       300000
#define MIN_ARRAY_LEN           3
#define MAX_ARRAY_LEN           30000000

/* Upper limit used for generation of random numbers */
#define UPPER_LIMIT             50000000

/* Comparison function passed to qsort() */
static int compare(const void *a, const void *b)
{
    if (*(const int32_t *)a > *(const int32_t *)b) {
        return 1;
    } else if (*(const int32_t *)a < *(const int32_t *)b) {
        return -1;
    }
    return 0;
}

int mock_main(int argc, char *argv[])
{
    int32_t *array_to_be_sorted;
    int32_t array_len = DEFAULT_ARRAY_LEN;
    int32_t option;

    /* Parse command line options */
    while ((option = getopt(argc, argv, "n:")) != -1) {
        if (option == 'n') {
            int32_t user_array_len = atoi(optarg);

            /* Check if the value is a string or zero */
            if (user_array_len == 0) {
                fprintf(stderr, "Error ... Invalid value for option '-n'.\n");
                exit(EXIT_FAILURE);
            }
            /* Check if the value is a negative number */
            if (user_array_len < MIN_ARRAY_LEN) {
                fprintf(stderr, "Error ... Value for option '-n' cannot be a "
                                "number less than %d.\n", MIN_ARRAY_LEN);
                exit(EXIT_FAILURE);
            }
            /* Check if the value is too large */
            if (user_array_len > MAX_ARRAY_LEN) {
                fprintf(stderr, "Error ... Value for option '-n' cannot be "
                                "more than %d.\n", MAX_ARRAY_LEN);
                exit(EXIT_FAILURE);
            }
            array_len = user_array_len;
        } else {
            exit(EXIT_FAILURE);
        }
    }

    /* Allocate the memory space for the array */
    array_to_be_sorted = (int32_t *) malloc(array_len * sizeof(int32_t));

    /* Populate the_array with random numbers */
    srand(1);
    for (size_t i = 0; i < array_len; i++) {
        array_to_be_sorted[i] = (rand()) / (RAND_MAX / UPPER_LIMIT);
    }

    /* Sort the_array using qsort() */
    qsort(array_to_be_sorted, array_len, sizeof(array_to_be_sorted[0]),
          compare);

    /* Control printing */
    printf("CONTROL RESULT:\n");
    printf("%d %d %d\n",
           array_to_be_sorted[0], array_to_be_sorted[1], array_to_be_sorted[2]);

    /* Free all previously allocated space */
    free(array_to_be_sorted);
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