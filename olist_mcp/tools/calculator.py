"""Calculator Tools (3 tools).

Complementary mathematical tools for post-query analysis.
"""

from __future__ import annotations
from typing import Literal
from fastmcp import FastMCP

def register(mcp: FastMCP) -> None:
    """Register 3 calculator tools on the MCP server."""

    @mcp.tool()
    def math_operation(
        a: float,
        b: float,
        operation: Literal["add", "sub", "mul", "div", "pow"] = "add"
    ) -> str:
        """Perform a basic mathematical operation between two numbers.
        
        Operations: add (+), sub (-), mul (*), div (/), pow (**).
        """
        try:
            if operation == "add":
                res = a + b
                symbol = "+"
            elif operation == "sub":
                res = a - b
                symbol = "-"
            elif operation == "mul":
                res = a * b
                symbol = "*"
            elif operation == "div":
                if b == 0:
                    return "**Error:** Division by zero."
                res = a / b
                symbol = "/"
            elif operation == "pow":
                res = a ** b
                symbol = "**"
            else:
                return f"**Error:** Invalid operation '{operation}'."
            
            return f"### Math Result\n\n{a} {symbol} {b} = **{res:,.4f}**"
        except Exception as e:
            return f"**Error:** {str(e)}"

    @mcp.tool()
    def percentage_calc(
        value: float,
        total: float,
        operation: Literal["get_percentage", "add_percentage", "sub_percentage"] = "get_percentage"
    ) -> str:
        """Perform percentage-based calculations.
        
        - get_percentage: What % is 'value' of 'total'?
        - add_percentage: Add 'value'% to 'total'.
        - sub_percentage: Subtract 'value'% from 'total'.
        """
        try:
            if operation == "get_percentage":
                if total == 0:
                    return "**Error:** Cannot calculate percentage of zero total."
                res = (value / total) * 100
                return f"### Percentage Result\n\n{value} is **{res:.2f}%** of {total}."
            
            elif operation == "add_percentage":
                res = total * (1 + value / 100)
                return f"### Percentage Result\n\n{total} + {value}% = **{res:,.4f}**"
            
            elif operation == "sub_percentage":
                res = total * (1 - value / 100)
                return f"### Percentage Result\n\n{total} - {value}% = **{res:,.4f}**"
            
            return f"**Error:** Invalid operation '{operation}'."
        except Exception as e:
            return f"**Error:** {str(e)}"

    @mcp.tool()
    def calculate_growth(new_value: float, old_value: float) -> str:
        """Calculate the percentage growth rate from old_value to new_value."""
        try:
            if old_value == 0:
                return "**Error:** Cannot calculate growth from zero base."
            growth = ((new_value - old_value) / abs(old_value)) * 100
            diff = new_value - old_value
            direction = "increase" if growth >= 0 else "decrease"
            
            return (
                f"### Growth Analysis\n\n"
                f"- **Old Value:** {old_value:,.2f}\n"
                f"- **New Value:** {new_value:,.2f}\n"
                f"- **Absolute Change:** {diff:+,.2f}\n"
                f"- **Growth Rate:** **{growth:+.2f}%** ({direction})"
            )
        except Exception as e:
            return f"**Error:** {str(e)}"
