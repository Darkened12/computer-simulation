; count_to_ten.asm
;
; this script increments the `counter` variable until it is equal to `desiredValue`'s value
;
;

section .data
    counter = 0
    desiredValue = 255


section .text
    ld ax, counter          ; adding counter to the A register
    ld bx, desiredValue     ; loading the desiredValue to the B register

    inc ax                  ; incrementing 1 to A register
    jne $2                  ; then checking if A register is equal to B, if not, loop back to the add operation
