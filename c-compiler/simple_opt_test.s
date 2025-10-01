.section .text
.global _start

_start:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    subq $24, %rsp                 # allocate local variable space
    movq $5, %rax                  # load integer 5
    movq %rax, -8(%rbp)            # store x
    movq -8(%rbp), %rax            # load x
    movq %rax, -16(%rbp)           # store y
    movq -16(%rbp), %rax           # load y
    movq %rax, -24(%rbp)           # store z
    movq -24(%rbp), %rax           # load z
    jmp main_epilogue              # return from function
main_epilogue:
    mov $60, %rax                  # exit syscall
    mov $0, %rdi                   # exit status 0
    syscall                        # invoke system call