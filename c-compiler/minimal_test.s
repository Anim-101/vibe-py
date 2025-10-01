.section .text
.global _start
.section .data
x: .quad 5
.section .text

add:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    movq %rdi, -8(%rbp)            # store parameter a
    movq %rsi, -16(%rbp)           # store parameter b
    movq -8(%rbp), %rax            # load a
    movq -16(%rbp), %rbx           # load b
    addq %rbx, %rax                # add operation
    jmp add_epilogue               # return from function
add_epilogue:
    movq %rbp, %rsp                # restore stack pointer
    popq %rbp                      # restore old base pointer
    ret                            # return to caller

_start:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    subq $8, %rsp                  # allocate local variable space
    movq x(%rip), %rax             # load global x
    movq %rax, %rdi                # pass argument 0
    movq $10, %rax                 # load integer 10
    movq %rax, %rsi                # pass argument 1
    call add                       # call function add
    movq %rax, -8(%rbp)            # store result
    movq $0, %rax                  # load integer 0
    jmp main_epilogue              # return from function
main_epilogue:
    mov $60, %rax                  # exit syscall
    mov $0, %rdi                   # exit status 0
    syscall                        # invoke system call