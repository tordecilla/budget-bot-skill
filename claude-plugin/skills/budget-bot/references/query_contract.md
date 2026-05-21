# Budget Bot Query Contract

Use exact budget labels from the lookup JSON or actual SQLite data before filtering departments or agencies.

Default to the latest available year when the user does not specify a year. Do not compare multiple years unless the user asks.

For multi-year comparisons, apply the same filters to each year and disclose any normalized names.

Always state:

- source database or source file,
- year or years,
- fields searched,
- exact filters or text terms,
- row count when helpful for auditability,
- totals in full pesos.

Use `AMT * 1000` for full-peso values. Keep source `AMT` in mind as thousands of pesos.

Use exact equality for `UACS_DPT_DSC`, `UACS_AGY_DSC`, `UACS_EXP_DSC`, and `UACS_FUNDSUBCAT_DSC` after resolving names. Use text search for `DSC`, `UACS_OPER_DSC`, and object descriptions.


