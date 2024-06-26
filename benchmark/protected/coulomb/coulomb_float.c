/*
 *  Source file of a benchmark program that computes the net forces acting on
 *  all n electrons randomly scattered across a 1m x 1m surface.
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
 */

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

/* Number of electrons on the surface */
#define NUMBER_OF_ELECTRONS 1000
#define MAX_NUMBER_OF_ELECTRONS 2000000000

/* Define Coulomb constant K, Electron charge Q, and PI */
const float K = 8987551792.3, Q = 0.0000000000000000001602176634,
            PI = 3.141592653589793;

/**
 * A struct for an Electron object.
 * It stores the particle position and electrical properties.
 */
struct Electron {
    /**
     * The X-coordinate of the electron position.
     */
    float x;
    /**
     * The Y-coordinate of the electron position.
     */
    float y;
    /**
     * The X-component of all electrical forces acting on the electron.
     */
    float Fx;
    /**
     * The Y-component of all electrical forces acting on the electron.
     */
    float Fy;
    /**
     * The magnitude of the net electrical forces acting on the electron.
     */
    float Fnet;
    /**
     * The angle of the net electrical forces acting on the electron.
     * It's the degree angle made with the positive direction of the X-axis.
     */
    float angle;
};

/**
 * Populate a surface (array of Electron objects) with electrons.
 * Electrons are placed at random positions ranging from (0, 0) to (1, 1)
 * It also initializes all other properties.
 * @param surface A pointer to an array of Electron objects.
 * @param number_of_electrons Number of electrons on the surface.
 */
void populate_surface(struct Electron *surface, int number_of_electrons)
{
    for (size_t i = 0; i < number_of_electrons; i++) {
        surface[i].x = rand() / (float)RAND_MAX;
        surface[i].y = rand() / (float)RAND_MAX;
        surface[i].Fx = 0;
        surface[i].Fy = 0;
        surface[i].Fnet = 0;
        surface[i].angle = 0;
    }
}

/**
 * Calculate the squared distance between two electron particles.
 * @param e1 A pointer to the first Electron object.
 * @param e2 A pointer to the second Electron object.
 * @return The euclidian squared distance between the two electrons.
 */
float calculate_distance_square(struct Electron const *e1,
                                struct Electron const *e2)
{
    /* (x1-x2)^2 + (y1-y2)^2 */
    return ((*e1).x - (*e2).x) * ((*e1).x - (*e2).x) +
           ((*e1).y - (*e2).y) * ((*e1).y - (*e2).y);
}

/**
 * Calculate the angle of the force acting on an Electron object e1 by another
 * e2.
 * @param e1 A pointer to the first Electron object, the one whose force angle
 * is returned.
 * @param e2 A pointer to the second Electron object.
 * @return The angle in radians.
 */
float calculate_angle(struct Electron const *e1, struct Electron const *e2)
{
    float delta_x = (*e2).x - (*e1).x;
    float delta_y = (*e2).y - (*e1).y;

    /* Calculate the angle in radians of the force acting on e1 */
    float alpha =
        (*e2).x == (*e1).x ? PI / 2.0 : atanf(fabs(delta_y / delta_x));

    /* First coordinate */
    if ((delta_x < 0 && (*e2).y == (*e1).y) || (delta_x < 0 && delta_y < 0)) {
        return alpha;
    }
    /* Second coordinate */
    else if (((*e2).x == (*e1).x && delta_y < 0) ||
             (delta_x > 0 && delta_y < 0)) {
        return PI - alpha;
    }
    /* Third coordinate */
    else if ((delta_x > 0 && (*e2).y == (*e1).y) ||
             (delta_x > 0 && delta_y > 0)) {
        return PI + alpha;
    }
    /* Fourth coordinate */
    /* (((*e2).x == (*e1).x && delta_y > 0) || (delta_x < 0 && delta_y > 0)) */
    else {
        return 2 * PI - alpha;
    }
}

/**
 * Update force components (Fx, Fy) for two electron particles.
 * @param e1 A pointer to the first Electron object.
 * @param e2 A pointer to the second Electron object.
 */
void calculate_force_components(struct Electron *e1, struct Electron *e2)
{
    /* Calculate force magnitude */
    float force_magnitude = K * Q * Q / calculate_distance_square(e1, e2);
    /* Calculate force direction on e1 by e2 */
    float angle = calculate_angle(e1, e2);
    /* Update the values of net forces in the two electrons (e2 = -e1) */
    (*e1).Fx += cosf(angle) * force_magnitude;
    (*e2).Fx -= (*e1).Fx;
    (*e1).Fy += sinf(angle) * force_magnitude;
    (*e2).Fy -= (*e1).Fy;
}

/**
 * Calculate net force magnitude and direction acting on an electron particle
 * @param e A pointer to an Electron object.
 */
void calculate_net_force(struct Electron *e)
{
    /* Fnet = sqrt(Fx^2 + Fy^2) */
    /* Using hypot() instead of sqrt() solves underflow in case of floats */
    (*e).Fnet = hypotf((*e).Fx, (*e).Fy);

    /* Angle = Tan^-1(Fy/Fx) */
    float angle = (*e).Fx == 0 ? PI / 2.0 : atan2f((*e).Fy, (*e).Fx);
    /* If angle is negative, add 2PI */
    if (angle < 0) {
        angle += 2 * PI;
    }
    /* Convert angle to degrees */
    (*e).angle = angle * 180 / PI;
}

int mock_main(int argc, char *argv[])
{
    int number_of_electrons = NUMBER_OF_ELECTRONS;
    int option;

    /* Parse command line options */
    while ((option = getopt(argc, argv, "n:")) != -1) {
        if (option == 'n') {
            int user_number_of_electrons = atoi(optarg);
            /* Check if the value is a string or zero */
            if (user_number_of_electrons == 0) {
                fprintf(stderr, "Error ... Invalid value for option '-n'.\n");
                exit(EXIT_FAILURE);
            }
            /* Check if the value is a negative number */
            if (user_number_of_electrons < 1) {
                fprintf(stderr, "Error ... Value for option '-n' cannot be a "
                                "negative number.\n");
                exit(EXIT_FAILURE);
            }
            /* Check if the value is too large */
            if (user_number_of_electrons > MAX_NUMBER_OF_ELECTRONS) {
                fprintf(stderr,
                        "Error ... Value for option '-n' cannot be "
                        "more than %d.\n",
                        MAX_NUMBER_OF_ELECTRONS);
                exit(EXIT_FAILURE);
            }
            number_of_electrons = user_number_of_electrons;
        } else {
            exit(EXIT_FAILURE);
        }
    }

    /* Seed random function with constant value */
    srand(1);
    /* Declare an array of Electron objects (surface) */
    struct Electron surface[number_of_electrons];
    /* Initialize all electrons on the surface */
    populate_surface(surface, number_of_electrons);
    /* Loop on all electrons on the surface and calculate */
    for (size_t i = 0; i < number_of_electrons; i++) {
        for (size_t j = i + 1; j < number_of_electrons; j++) {
            /*
             * Update the forces components for the two electrons located at
             * surface[i] and surface[j]
             */
            calculate_force_components(&surface[i], &surface[j]);
        }
        /*
         * Calculate and print the net electrostatic forces on electron located
         * at surface[i]
         */
        calculate_net_force(&surface[i]);
        printf("-------------------------------------\n");
        printf("Electron at (%.4f, %.4f):\n    Net Force: %.10G Newtons\n    "
               "Angle: %.3f°\n",
               surface[i].x, surface[i].y, surface[i].Fnet, surface[i].angle);
    }
    printf("-------------------------------------\n");
    return 0;
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