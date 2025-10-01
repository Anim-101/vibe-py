.section .text
.global _start

compute_value:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    subq $8, %rsp                  # allocate local variable space
    movq $14, %rax                 # load integer 14
    movq %rax, -8(%rbp)            # store result
    movq -8(%rbp), %rax            # load result
    movq %rax, -8(%rbp)            # assign to result
    movq -8(%rbp), %rbx            # load result
    movq %rbx, -8(%rbp)            # assign to result
    movq -8(%rbp), %rcx            # load result
    movq %rcx, %rax                # move return value to rax
    jmp compute_value_epilogue     # return from function
    movq $-1, %rcx                 # load integer -1
    movq %rcx, %rax                # move return value to rax
    jmp compute_value_epilogue     # return from function
compute_value_epilogue:
    movq %rbp, %rsp                # restore stack pointer
    popq %rbp                      # restore old base pointer
    ret                            # return to caller

test_loops:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    subq $16, %rsp                 # allocate local variable space
    movq $0, %rax                  # load integer 0
    movq %rax, -8(%rbp)            # store sum
    movq $0, %rax                  # load integer 0
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
    addq $1, %rbx                # combined add immediate
    jmp while_start1               # repeat loop
while_end2:
    movq -8(%rbp), %rcx            # load sum
    movq %rcx, %rax                # move return value to rax
    jmp test_loops_epilogue        # return from function
test_loops_epilogue:
    movq %rbp, %rsp                # restore stack pointer
    popq %rbp                      # restore old base pointer
    ret                            # return to caller

_start:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    subq $40, %rsp                 # allocate local variable space
    movq $15, %rax                 # load integer 15
    movq %rax, -8(%rbp)            # store x
    movq $0, %rax                  # load integer 0
    movq %rax, -16(%rbp)           # store y
    movq -8(%rbp), %rax            # load x
    movq %rax, -24(%rbp)           # store z
    call compute_value             # call function compute_value
    movq %rax, -32(%rbp)           # store result1
    call test_loops                # call function test_loops
    movq %rax, -40(%rbp)           # store result2
    movq -32(%rbp), %rax           # load result1
    movq -40(%rbp), %rbx           # load result2
    addq %rbx, %rax                # add operation
    jmp main_epilogue              # return from function
main_epilogue:
    mov $60, %rax                  # exit syscall
    mov $0, %rdi                   # exit status 0
    syscall                        # invoke system call