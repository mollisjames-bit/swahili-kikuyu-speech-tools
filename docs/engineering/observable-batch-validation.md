# A successful batch can still reject most of its records

Signal Data Partners technical sample, 1 October 2026. AI-assisted writing and code, checked by execution against synthetic records. This is a teaching fixture, not a report of a customer deployment.

A background import can finish without crashing while rejecting nearly every input row. The process exit code answers whether the program completed. It does not answer whether the imported data was useful. If your monitoring reports only successful executions, a validation problem can remain invisible behind a healthy jobs counter.

Start by deciding which outcome the operator needs to see. For the demonstration below, the important questions are how many rows arrived, how many were accepted, how many were rejected, and which validation rules fired. These are different quantities. A row that fails three rules counts as one rejected row and three rule failures.

## Run the example

Save this code as `observable-batch-validation.cjs` and run `node observable-batch-validation.cjs` with Node.js 18 or later. It uses only Node's built-in assertion module. The inputs deliberately contain a duplicate identifier, an inconsistent amount, an absent identifier and an absent currency.

```javascript
'use strict';
const assert = require('node:assert/strict');

function summarizeBatch(records) {
  const seen = new Set();
  const ruleCounts = {missing_id:0, duplicate_id:0, missing_currency:0, arithmetic_mismatch:0};
  let rejected = 0;
  for (const row of records) {
    let invalid = false;
    const mark = name => {ruleCounts[name]++; invalid = true;};
    if (!row.id) mark('missing_id');
    else if (seen.has(row.id)) mark('duplicate_id');
    else seen.add(row.id);
    if (!row.currency) mark('missing_currency');
    const values = [row.amount, row.quantity, row.unitPrice];
    if (!values.every(Number.isFinite) ||
        Math.abs(row.amount - row.quantity * row.unitPrice) > 0.005) {
      mark('arithmetic_mismatch');
    }
    if (invalid) rejected++;
  }
  return {event:'validation_batch_completed', rows_seen:records.length,
    rows_accepted:records.length-rejected, rows_rejected:rejected,
    rejection_ratio:records.length ? rejected/records.length : null,
    rule_counts:ruleCounts};
}

const fixture = [
  {id:'A1',amount:120,currency:'USD',quantity:2,unitPrice:60},
  {id:'A1',amount:120,currency:'USD',quantity:2,unitPrice:60},
  {id:'A2',amount:90,currency:'USD',quantity:2,unitPrice:40},
  {id:'',amount:50,currency:'USD',quantity:1,unitPrice:50},
  {id:'A3',amount:10,currency:'',quantity:1,unitPrice:10}
];
const result = summarizeBatch(fixture);
assert.equal(result.rows_seen,5);
assert.equal(result.rows_accepted,1);
assert.equal(result.rows_rejected,4);
assert.equal(result.rejection_ratio,0.8);
assert.equal(summarizeBatch([]).rejection_ratio,null);
const multi = summarizeBatch([{id:'',amount:90,currency:'',quantity:2,unitPrice:40}]);
assert.equal(multi.rows_rejected,1);
assert.equal(Object.values(multi.rule_counts).reduce((a,b)=>a+b,0),3);
assert.equal(JSON.stringify(result).includes('A1'),false);
console.log(JSON.stringify({fixture:'synthetic demonstration',checks_passed:8,...result},null,2));
```

The output contains five seen rows, one accepted row, four rejected rows and a rejection ratio of 0.8. The four named rule counters each equal one. Eight assertions check the main result, the empty batch, a row that fails three rules and the absence of a sample identifier from the summary.

The empty batch returns a null ratio. Returning zero would imply that real inputs were checked and passed. If the system expects an input batch, an operator also needs a separate missing-input or zero-volume signal.

## Count outcomes and failures separately

The inner `mark` function updates a rule counter and marks the current row invalid. Only after all rules have run does the program increment `rejected`. This prevents double-counting a row with several errors. The invariant is `accepted + rejected = seen`; it is not `sum(rule failures) = rejected`.

The repeated identifier is detected inside this one batch. A real importer needs to define whether duplicates also mean identifiers already stored in its database. That requires a different state boundary. The example also accepts a small absolute arithmetic tolerance for its simple demonstration; real money workflows should use a domain-approved decimal representation and rounding rule.

## Export the summary instead of the record

The JSON output contains an event name, counts, a ratio and a fixed set of rule categories. It contains no row identifiers, record amounts or free-text record content. This gives the operator a small aggregate signal while keeping the row-level investigation in its separate, access-controlled workflow.

This is not a complete confidentiality guarantee. File names, database errors, tracing attributes and exception stack messages can still expose content elsewhere in a real system. The useful design choice here is to build a narrow summary object intentionally rather than log the input and attempt to redact it later.

## Connect the outcomes to monitoring

In a commissioned implementation, the seen, accepted and rejected counts can become counter measurements. The fixed rule names can label a separate rule-failure counter. Duration is a different measurement and belongs in a histogram. A unique row or job identifier should not become a metric label: it creates a fresh time series rather than a reusable category.

When combining batches, calculate `sum(rejected) / sum(seen)` over the same interval. Do not average per-batch ratios: a one-row batch and a thousand-row batch would otherwise carry equal weight. Do not alert on the ratio alone; combine it with an appropriate minimum input volume and the job's expected delivery window.

The runnable example above emits ordinary JSON to stdout. It does not configure an OpenTelemetry SDK, collector, SigNoz dashboard or alert. Those are separate integration steps, and their acceptance evidence should include the telemetry received at the backend and a deliberately injected validation failure.

Source for instrument concepts: [OpenTelemetry metrics documentation](https://opentelemetry.io/docs/concepts/signals/metrics/). The implementation and assertions above are our synthetic demonstration.
