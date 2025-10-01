.section .text
.global _start

calculate_complex:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    subq $56, %rsp                 # allocate local variable space
    movq %rdi, -8(%rbp)            # store parameter a
    movq %rsi, -16(%rbp)           # store parameter b
    movq %rdx, -24(%rbp)           # store parameter c
    movq %rcx, -32(%rbp)           # store parameter d
    addq %rsi, %rdi                # add operation
    movq %rdi, -40(%rbp)           # store x
    imulq %rcx, %rdx               # multiply operation
    movq %rdx, -48(%rbp)           # store y
    subq %r12, %rbx                # subtract operation
    movq %rbx, -56(%rbp)           # store z
    addq %r12, %rbx                # add operation
    addq %r13, %rbx                # add operation
    movq %rbx, -64(%rbp)           # store w
    movq $2, %rax                  # load integer 2
    imulq %rax, %r14               # multiply operation
    movq %r14, -72(%rbp)           # store v
    addq %rdi, %r15                # add operation
    subq %rsi, %r15                # subtract operation
    movq %r15, -80(%rbp)           # store u
    movq $100, %rax                # load integer 100
    cmpq %rax, %r10                # compare for greater than
    setg %al                       # set result of comparison
    movzbq %al, %r10               # zero-extend result
    testq %r10, %r10               # test condition
    jz else1                       # jump if false
    movq $2, %rax                  # load integer 2
    movq %r10, -88(%rbp)           # store temp
    addq %rbx, %r11                # add operation
    movq %r11, %rax                # move return value to rax
    jmp calculate_complex_epilogue # return from function
    jmp end_if2                    # skip else part
else1:
end_if2:
    addq %r13, %r10                # add operation
    movq %r10, %rax                # move return value to rax
    jmp calculate_complex_epilogue # return from function
calculate_complex_epilogue:
    movq %rbp, %rsp                # restore stack pointer
    popq %rbp                      # restore old base pointer
    ret                            # return to caller

test_register_pressure:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    subq $88, %rsp                 # allocate local variable space
    movq $1, %rax                  # load integer 1
    movq %rax, -96(%rbp)           # store a
    movq $2, %rax                  # load integer 2
    movq %rax, -104(%rbp)          # store b
    movq $3, %rax                  # load integer 3
    movq %rax, -112(%rbp)          # store c
    movq $4, %rax                  # load integer 4
    movq %rax, -120(%rbp)          # store d
    movq $5, %rax                  # load integer 5
    movq %rax, -128(%rbp)          # store e
    movq $6, %rax                  # load integer 6
    movq %rax, -136(%rbp)          # store f
    movq $7, %rax                  # load integer 7
    movq %rax, -144(%rbp)          # store g
    movq $8, %rax                  # load integer 8
    movq %rax, -152(%rbp)          # store h
    movq $9, %rax                  # load integer 9
    movq %rax, -160(%rbp)          # store i
    movq $10, %rax                 # load integer 10
    movq %rax, -168(%rbp)          # store j
    addq %rsi, %rdi                # add operation
    addq %rdx, %rdi                # add operation
    addq %rcx, %rdi                # add operation
    addq %r8, %rdi                 # add operation
    addq %r9, %rdi                 # add operation
    addq %rbx, %rdi                # add operation
    addq %rbx, %rdi                # add operation
    addq %rbx, %rdi                # add operation
    addq %rbx, %rdi                # add operation
    movq %rdi, -176(%rbp)          # store result
    movq $2, %rax                  # load integer 2
    imulq %rax, %rbx               # multiply operation
    movq %rbx, %rdi                # assign to a
    addq %rbx, %rdi                # add operation
    movq %rdi, %rsi                # assign to b
    movq %rsi, %rax                # move return value to rax
    jmp test_register_pressure_epilogue # return from function
test_register_pressure_epilogue:
    movq %rbp, %rsp                # restore stack pointer
    popq %rbp                      # restore old base pointer
    ret                            # return to caller

_start:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    subq $24, %rsp                 # allocate local variable space
    movq $10, %rax                 # load integer 10
    movq %rax, %rdi                # pass argument 0
    movq $20, %rax                 # load integer 20
    movq %rax, %rsi                # pass argument 1
    movq $30, %rax                 # load integer 30
    movq %rax, %rdx                # pass argument 2
    movq $40, %rax                 # load integer 40
    movq %rax, %rcx                # pass argument 3
    call calculate_complex         # call function calculate_complex
    movq %rax, -184(%rbp)          # store result1
    call test_register_pressure    # call function test_register_pressure
    movq %rax, -192(%rbp)          # store result2
    addq %rbx, %rbx                # add operation
    movq %rbx, -200(%rbp)          # store final
    movq %rbx, %rax                # move return value to rax
    jmp main_epilogue              # return from function
main_epilogue:
    mov $60, %rax                  # exit syscall
    mov $0, %rdi                   # exit status 0
    syscall                        # invoke system call