; count_to_ten.asm
;
; this script increments the `counter` variable until it is equal to `desiredValue`'s value
;
;

section .data
    counter = 0
    desiredValue = 10
    increment = 1


section .text
    ld ax, counter          ; adding counter to the A register
    ld bx, increment        ; number to add to register A

    add bx, ax              ; adding B register to A register
    mov ax, counter         ; storing the value of the A register to the counter variable
    ld bx, desiredValue     ; loading the desiredValue to the B register
    jne $2                  ; then checking if A register is equal to B, if not, loop back to the add operation

