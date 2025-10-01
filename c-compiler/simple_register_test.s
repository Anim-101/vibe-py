.section .text
.global _start

compute:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    subq $24, %rsp                 # allocate local variable space
    movq %rdi, -8(%rbp)            # store parameter a
    movq %rsi, -16(%rbp)           # store parameter b
    addq %rsi, %rdi                # add operation
    movq %rdi, -24(%rbp)           # store x
    movq $2, %rax                  # load integer 2
    imulq %rax, %rbx               # multiply operation
    movq %rbx, -32(%rbp)           # store y
    subq %rdi, %r12                # subtract operation
    movq %r12, -40(%rbp)           # store z
    movq %r13, %rax                # move return value to rax
    jmp compute_epilogue           # return from function
compute_epilogue:
    movq %rbp, %rsp                # restore stack pointer
    popq %rbp                      # restore old base pointer
    ret                            # return to caller

_start:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    subq $8, %rsp                  # allocate local variable space
    movq $10, %rax                 # load integer 10
    movq %rax, %rdi                # pass argument 0
    movq $20, %rax                 # load integer 20
    movq %rax, %rsi                # pass argument 1
    call compute                   # call function compute
    movq %rax, -48(%rbp)           # store result
    movq %r14, %rax                # move return value to rax
    jmp main_epilogue              # return from function
main_epilogue:
    mov $60, %rax                  # exit syscall
    mov $0, %rdi                   # exit status 0
    syscall                        # invoke system call