.section .text
.global _start

_start:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    subq $8, %rsp                  # allocate local variable space
    movq $5, %rax                  # load integer 5
    movq %rax, %rdi                # pass argument 0
    call conditional_constants     # call function conditional_constants
    movq %rax, -8(%rbp)            # store c
    movq $171, %rax                # load integer 171
    addq %rbx, %rax                # add operation
    addq $300, %rax                # combined add immediate
    addq %rbx, %rax                # add operation
    jmp main_epilogue              # return from function
main_epilogue:
    mov $60, %rax                  # exit syscall
    mov $0, %rdi                   # exit status 0
    syscall                        # invoke system call