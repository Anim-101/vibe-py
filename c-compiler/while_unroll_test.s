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
while_start1:
    movq -16(%rbp), %rax           # load i
    movq $3, %rbx                  # load integer 3
    cmpq %rbx, %rax                # compare for less than
    setl %al                       # set result of comparison
    movzbq %al, %rax               # zero-extend result
    testq %rax, %rax               # test loop condition
    jz while_end2                  # exit if false
    movq -16(%rbp), %rax           # load i
    addq %rax, %rbx                # add operation
    movq -16(%rbp), %rax           # load i
    addq $1, %rax                # combined add immediate
    jmp while_start1               # repeat loop
while_end2:
    movq %rbx, %rax                # move return value to rax
    jmp main_epilogue              # return from function
main_epilogue:
    mov $60, %rax                  # exit syscall
    mov $0, %rdi                   # exit status 0
    syscall                        # invoke system call