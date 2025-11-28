'use client'

import * as React from 'react'
import { ButtonProps, buttonVariants } from './button'

function cn(...inputs: Array<string | null | undefined | false>) {
  return inputs.filter(Boolean).join(' ')
}

const ModernButton = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, children, disabled, ...props }, ref) => {
    return (
      <button
        className={cn(
          buttonVariants({ variant, size, className }),
          'relative overflow-hidden transition-all duration-300 transform hover:scale-105 active:scale-95'
        )}
        ref={ref}
        disabled={disabled}
        {...props}
      >
        <span className="relative z-10 flex items-center justify-center space-x-2">
          {disabled && <span className="animate-spin">⟳</span>}
          {children}
        </span>
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] hover:translate-x-[100%] transition-transform duration-700" />
      </button>
    )
  }
)
ModernButton.displayName = 'ModernButton'

export { ModernButton, buttonVariants }
