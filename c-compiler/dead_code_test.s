.section .text
.global _start

function_with_unused_vars:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    subq $8, %rsp                  # allocate local variable space
    movq %rdi, -8(%rbp)            # store parameter x
    movq $20, %rax                 # load integer 20
    movq %rax, -16(%rbp)           # store used_var
    movq $40, %rax                 # load integer 40
    movq %rax, dead_store(%rip)    # assign to global dead_store
    addq %rdi, %rbx                # add operation
    movq %rbx, %rax                # move return value to rax
    jmp function_with_unused_vars_epilogue # return from function
function_with_unused_vars_epilogue:
    movq %rbp, %rsp                # restore stack pointer
    popq %rbp                      # restore old base pointer
    ret                            # return to caller

function_with_constant_conditions:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    movq %rdi, -24(%rbp)           # store parameter x
    addq $1, %rdi                # combined add immediate
    jmp function_with_constant_conditions_epilogue # return from function
function_with_constant_conditions_epilogue:
    movq %rbp, %rsp                # restore stack pointer
    popq %rbp                      # restore old base pointer
    ret                            # return to caller

_start:
    pushq %rbp                     # save old base pointer
    movq %rsp, %rbp                # establish new base pointer
    subq $8, %rsp                  # allocate local variable space
    movq $5, %rbx                  # load integer 5
    movq %rbx, %rdi                # pass argument 0
    call function_with_unreachable_code # call function function_with_unreachable_code
    movq %rax, -32(%rbp)           # store result
    movq %r12, %rdi                # pass argument 0
    call function_with_unused_vars # call function function_with_unused_vars
    movq %rax, %r12                # assign to result
    movq %r12, %rdi                # pass argument 0
    call function_with_constant_conditions # call function function_with_constant_conditions
    movq %rax, %r12                # assign to result
    movq %r12, %rax                # move return value to rax
    jmp main_epilogue              # return from function
main_epilogue:
    mov $60, %rax                  # exit syscall
    mov $0, %rdi                   # exit status 0
    syscall                        # invoke system call