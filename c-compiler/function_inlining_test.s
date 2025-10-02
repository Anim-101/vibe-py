.section .text
.global _start

add:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    movq %rdi, -8(%rbp)            # store parameter a
    movq %rsi, -16(%rbp)           # store parameter b
    addq %rsi, %rdi                # add operation
    movq %rdi, %rax                # move return value to rax
    jmp add_epilogue               # return from function
add_epilogue:
    movq %rbp, %rsp                # restore stack pointer
    popq %rbp                      # restore old base pointer
    ret                            # return to caller

multiply:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    movq %rdi, -24(%rbp)           # store parameter x
    movq %rsi, -32(%rbp)           # store parameter y
    imulq %rsi, %rdi               # multiply operation
    movq %rdi, %rax                # move return value to rax
    jmp multiply_epilogue          # return from function
multiply_epilogue:
    movq %rbp, %rsp                # restore stack pointer
    popq %rbp                      # restore old base pointer
    ret                            # return to caller

square:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    movq %rdi, -40(%rbp)           # store parameter n
    movq %rdi, %rsi                # pass argument 1
    call multiply                  # call function multiply
    jmp square_epilogue            # return from function
square_epilogue:
    movq %rbp, %rsp                # restore stack pointer
    popq %rbp                      # restore old base pointer
    ret                            # return to caller

complex_calculation:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    subq $8, %rsp                  # allocate local variable space
    movq %rdi, -48(%rbp)           # store parameter a
    movq %rsi, -56(%rbp)           # store parameter b
    movq %rdx, -64(%rbp)           # store parameter c
    movq $0, %rax                  # load integer 0
    movq %rax, -72(%rbp)           # store result
    movq $0, %rax                  # load integer 0
    cmpq %rax, %rdi                # compare for greater than
    setg %al                       # set result of comparison
    movzbq %al, %rdi               # zero-extend result
    testq %rdi, %rdi               # test condition
    jz else1                       # jump if false
    call add                       # call function add
    movq %rax, %rbx                # assign to result
    movq $5, %rax                  # load integer 5
    cmpq %rax, %rsi                # compare for greater than
    setg %al                       # set result of comparison
    movzbq %al, %rsi               # zero-extend result
    testq %rsi, %rsi               # test condition
    jz else3                       # jump if false
    movq %rbx, %rdi                # pass argument 0
    movq %rdx, %rsi                # pass argument 1
    call multiply                  # call function multiply
    movq %rax, %rbx                # assign to result
    jmp end_if4                    # skip else part
else3:
    addq %rdx, %rbx                # add operation
end_if4:
    jmp end_if2                    # skip else part
else1:
    movq %rdx, %rsi                # pass argument 1
    call multiply                  # call function multiply
    movq %rax, %rbx                # assign to result
end_if2:
    movq %rbx, %rax                # move return value to rax
    jmp complex_calculation_epilogue # return from function
complex_calculation_epilogue:
    movq %rbp, %rsp                # restore stack pointer
    popq %rbp                      # restore old base pointer
    ret                            # return to caller

_start:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    subq $64, %rsp                 # allocate local variable space
    movq $10, %rax                 # load integer 10
    movq %rax, -80(%rbp)           # store x
    movq $5, %rax                  # load integer 5
    movq %rax, -88(%rbp)           # store y
    call add                       # call function add
    movq %rax, -96(%rbp)           # store sum
    movq $3, %rax                  # load integer 3
    movq %rax, %rsi                # pass argument 1
    call multiply                  # call function multiply
    movq %rax, -104(%rbp)          # store prod
    movq $4, %rax                  # load integer 4
    movq %rax, %rdi                # pass argument 0
    call square                    # call function square
    movq %rax, -112(%rbp)          # store sq
    movq %r12, %rdi                # pass argument 0
    movq %r13, %rsi                # pass argument 1
    call add                       # call function add
    movq %rax, -120(%rbp)          # store sum2
    movq %r14, %rdi                # pass argument 0
    movq $2, %rax                  # load integer 2
    movq %rax, %rsi                # pass argument 1
    call multiply                  # call function multiply
    movq %rax, -128(%rbp)          # store prod2
    movq %r12, %rdx                # pass argument 2
    call complex_calculation       # call function complex_calculation
    movq %rax, -136(%rbp)          # store complex
    addq %r13, %r12                # add operation
    addq %r14, %r12                # add operation
    addq %r15, %r12                # add operation
    movq %r12, %rax                # move return value to rax
    jmp main_epilogue              # return from function
main_epilogue:
    mov $60, %rax                  # exit syscall
    mov $0, %rdi                   # exit status 0
    syscall                        # invoke system call