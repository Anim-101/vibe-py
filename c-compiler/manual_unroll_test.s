.section .text
.global _start

_start:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    subq $16, %rsp                 # allocate local variable space
    movq $0, %rax                  # load integer 0
    movq %rax, -8(%rbp)            # store sum
    movq $0, %rax                  # load integer 0
    movq %rax, -16(%rbp)           # store i
    addq $1, %rbx                # combined add immediate
    addq %rax, %rbx                # add operation
    addq $3, %rbx                # combined add immediate
    jmp main_epilogue              # return from function
main_epilogue:
    mov $60, %rax                  # exit syscall
    mov $0, %rdi                   # exit status 0
    syscall                        # invoke system call