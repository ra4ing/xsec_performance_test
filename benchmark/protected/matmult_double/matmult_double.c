/*
 *  Source file of a benchmark program involving calculations of
 *  a product of two matrixes nxn whose elements are "double". The
 *  number n can be given via command line, and the default is 200.
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

/* Number of columns and rows in all matrixes*/
#define DEFAULT_MATRIX_SIZE     200
#define MIN_MATRIX_SIZE         2
#define MAX_MATRIX_SIZE         200000

int mock_main(int argc, char *argv[])
{
    double **matrix_a;
    double **matrix_b;
    double **matrix_res;
    size_t i;
    size_t j;
    size_t k;
    int32_t matrix_size = DEFAULT_MATRIX_SIZE;
    int32_t option;
    double range_factor = 100.0 / (double)(RAND_MAX);


    /* Parse command line options */
    while ((option = getopt(argc, argv, "n:")) != -1) {
        if (option == 'n') {
            int32_t user_matrix_size = atoi(optarg);

            /* Check if the value is a string or zero */
            if (user_matrix_size == 0) {
                fprintf(stderr, "Error ... Invalid value for option '-n'.\n");
                exit(EXIT_FAILURE);
            }
            /* Check if the value is a negative number */
            if (user_matrix_size < MIN_MATRIX_SIZE) {
                fprintf(stderr, "Error ... Value for option '-n' cannot be a "
                                "number less than %d.\n", MIN_MATRIX_SIZE);
                exit(EXIT_FAILURE);
            }
            /* Check if the value is too large */
            if (user_matrix_size > MAX_MATRIX_SIZE) {
                fprintf(stderr, "Error ... Value for option '-n' cannot be "
                                "more than %d.\n", MAX_MATRIX_SIZE);
                exit(EXIT_FAILURE);
            }
            matrix_size = user_matrix_size;
        } else {
            exit(EXIT_FAILURE);
        }
    }

    /* Allocate the memory space for all matrixes */
    matrix_a = (double **)malloc(matrix_size * sizeof(double *));
    for (i = 0; i < matrix_size; i++) {
        matrix_a[i] = (double *)malloc(matrix_size * sizeof(double));
    }
    matrix_b = (double **)malloc(matrix_size * sizeof(double *));
    for (i = 0; i < matrix_size; i++) {
        matrix_b[i] = (double *)malloc(matrix_size * sizeof(double));
    }
    matrix_res = (double **)malloc(matrix_size * sizeof(double *));
    for (i = 0; i < matrix_size; i++) {
        matrix_res[i] = (double *)malloc(matrix_size * sizeof(double));
    }

    /* Populate matrix_a and matrix_b with random numbers */
    srand(1);
    for (i = 0; i < matrix_size; i++) {
        for (j = 0; j < matrix_size; j++) {
            matrix_a[i][j] = range_factor * (double)rand();
            matrix_b[i][j] = range_factor * (double)rand();
        }
    }

    /* Calculate the product of two matrixes */
    for (i = 0; i < matrix_size; i++) {
        for (j = 0; j < matrix_size; j++) {
            matrix_res[i][j] = 0.0;
            for (k = 0; k < matrix_size; k++) {
                matrix_res[i][j] += matrix_a[i][k] * matrix_b[k][j];
            }
        }
    }

    /* Control printing */
    printf("CONTROL RESULT:\n");
    printf(" %f %f\n", matrix_res[0][0], matrix_res[0][1]);
    printf(" %f %f\n", matrix_res[1][0], matrix_res[1][1]);

    /* Free all previously allocated space */
    for (i = 0; i < matrix_size; i++) {
        free(matrix_a[i]);
        free(matrix_b[i]);
        free(matrix_res[i]);
    }
    free(matrix_a);
    free(matrix_b);
    free(matrix_res);
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