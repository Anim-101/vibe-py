.section .text
.global _start

_start:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    subq $32, %rsp                 # allocate local variable space
    movq $15, %rax                 # load integer 15
    movq %rax, -8(%rbp)            # store a
    movq -8(%rbp), %rax            # load a
    movq %rax, -16(%rbp)           # store b
    movq -16(%rbp), %rax           # load b
    movq %rax, -24(%rbp)           # store c
    movq -24(%rbp), %rax           # load c
    movq %rax, -32(%rbp)           # store d
    movq -32(%rbp), %rax           # load d
    jmp main_epilogue              # return from function
    movq $-1, %rbx                 # load integer -1
    movq %rbx, %rax                # move return value to rax
    jmp main_epilogue              # return from function
main_epilogue:
    mov $60, %rax                  # exit syscall
    mov $0, %rdi                   # exit status 0
    syscall                        # invoke system call