from .. import schemas


def plan(input: schemas.BusinessPlanInput) -> schemas.BusinessPlanOutput:
    revenue = input.seats * input.average_check * input.open_days_per_month
    variable = revenue * input.variable_cost_rate
    opex = input.fixed_monthly_costs + variable
    margin_rate = 0.0 if revenue == 0 else (revenue - opex) / revenue
    monthly_profit = revenue - opex
    break_even_months = float('inf') if monthly_profit <= 0 else round(input.initial_capex / monthly_profit, 2)
    return schemas.BusinessPlanOutput(
        projected_monthly_revenue=round(revenue, 2),
        projected_monthly_opex=round(opex, 2),
        gross_margin_rate=round(margin_rate, 4),
        break_even_months=break_even_months,
    )
