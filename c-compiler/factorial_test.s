.section .text
.global _start

factorial:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    movq %rdi, -8(%rbp)            # store parameter n
    movq -8(%rbp), %rax            # load n
    movq $2, %rbx                  # load integer 2
    cmpq %rbx, %rax                # compare for less than
    setl %al                       # set result of comparison
    movzbq %al, %rax               # zero-extend result
    testq %rax, %rax               # test condition
    jz else1                       # jump if false
    movq $1, %rax                  # load integer 1
    jmp factorial_epilogue         # return from function
    jmp end_if2                    # skip else part
else1:
    movq -8(%rbp), %rbx            # load n
    movq -8(%rbp), %rcx            # load n
    movq $1, %rdx                  # load integer 1
    subq %rdx, %rcx                # subtract operation
    movq %rcx, %rdi                # pass argument 0
    call factorial                 # call function factorial
    imulq %rax, %rbx               # multiply operation
    movq %rbx, %rax                # move return value to rax
    jmp factorial_epilogue         # return from function
end_if2:
factorial_epilogue:
    movq %rbp, %rsp                # restore stack pointer
    popq %rbp                      # restore old base pointer
    ret                            # return to caller

_start:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    subq $16, %rsp                 # allocate local variable space
    movq $5, %rax                  # load integer 5
    movq %rax, -8(%rbp)            # store num
    movq -8(%rbp), %rax            # load num
    movq %rax, %rdi                # pass argument 0
    call factorial                 # call function factorial
    movq %rax, -16(%rbp)           # store result
    movq -16(%rbp), %rax           # load result
    movq $100, %rbx                # load integer 100
    cmpq %rbx, %rax                # compare for greater than
    setg %al                       # set result of comparison
    movzbq %al, %rax               # zero-extend result
    testq %rax, %rax               # test condition
    jz else3                       # jump if false
    movq $1, %rax                  # load integer 1
    jmp main_epilogue              # return from function
    jmp end_if4                    # skip else part
else3:
end_if4:
    movq $0, %rbx                  # load integer 0
    movq %rbx, %rax                # move return value to rax
    jmp main_epilogue              # return from function
main_epilogue:
    mov $60, %rax                  # exit syscall
    mov $0, %rdi                   # exit status 0
    syscall                        # invoke system call