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

_start:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    subq $16, %rsp                 # allocate local variable space
    movq $3, %rax                  # load integer 3
    movq %rax, %rdi                # pass argument 0
    movq $5, %rax                  # load integer 5
    movq %rax, %rsi                # pass argument 1
    call add                       # call function add
    movq %rax, -24(%rbp)           # store x
    movq %rbx, %rdi                # pass argument 0
    movq $2, %rax                  # load integer 2
    movq %rax, %rsi                # pass argument 1
    call add                       # call function add
    movq %rax, -32(%rbp)           # store y
    addq %r12, %rbx                # add operation
    movq %rbx, %rax                # move return value to rax
    jmp main_epilogue              # return from function
main_epilogue:
    mov $60, %rax                  # exit syscall
    mov $0, %rdi                   # exit status 0
    syscall                        # invoke system call