int global_argc;
char** global_argv;

void mock_help() {
    asm volatile (
        "addi sp, sp, -16\n\t"
        "sd ra, 8(sp)\n\t"
    );
    mock_main(global_argc, global_argv);
    // printf("mock_help_start\n");
    asm volatile (
        "ld ra, 8(sp)\n\t" 
        "addi sp, sp, 16\n\t"
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

        "ld ra, 8(sp)\n\t"
        "addi sp, sp, 16\n\t"
    );
    // printf("mock_func_end\n");
}

int main(int argc, char* argv[]) {
    global_argc = argc;
    global_argv = argv;
    mock_func();
    return 0;
}