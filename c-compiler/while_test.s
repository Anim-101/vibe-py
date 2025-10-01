.section .text
.global _start

_start:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    subq $16, %rsp                 # allocate local variable space
    movq $0, %rax                  # load integer 0
    movq %rax, -8(%rbp)            # store sum
    movq $1, %rax                  # load integer 1
    movq %rax, -16(%rbp)           # store i
while_start1:
    movq -16(%rbp), %rax           # load i
    movq $5, %rbx                  # load integer 5
    cmpq %rbx, %rax                # compare for less than
    setl %al                       # set result of comparison
    movzbq %al, %rax               # zero-extend result
    testq %rax, %rax               # test loop condition
    jz while_end2                  # exit if false
    movq -8(%rbp), %rax            # load sum
    movq -16(%rbp), %rbx           # load i
    addq %rbx, %rax                # add operation
    movq %rax, -8(%rbp)            # assign to sum
    movq -16(%rbp), %rbx           # load i
    movq $1, %rcx                  # load integer 1
    addq %rcx, %rbx                # add operation
    movq %rbx, -16(%rbp)           # assign to i
    jmp while_start1               # repeat loop
while_end2:
    movq -8(%rbp), %rcx            # load sum
    movq %rcx, %rax                # move return value to rax
    jmp main_epilogue              # return from function
main_epilogue:
    mov $60, %rax                  # exit syscall
    mov $0, %rdi                   # exit status 0
    syscall                        # invoke system call