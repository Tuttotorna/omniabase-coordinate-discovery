# Results

This file records the first experimental results for **Omniabase Coordinate Discovery**.

The purpose of this repository is not to use Omniabase as a truth gate, but as a multi-representation engine for discovering latent coordinates, regime signatures, and early transition markers in dynamical systems.

The first testbed is the logistic map.

---

## Experiment 1 — Logistic map multibase signatures v0

### System

Logistic map:

\[
x_{n+1} = r x_n (1 - x_n)
\]

### Initial settings

- system: logistic map
- initial state: `x0 = 0.123456`
- total iterations: `300`
- burn-in: `100`
- bases: `2` to `16`
- decimal precision per state: `12` digits

### Tested r values

- 3.50
- 3.55
- 3.60
- 3.70
- 3.80
- 3.90
- 4.00

### Extracted minimal signatures

For each state after burn-in, the prototype extracted:

- `avg_digit_sum`
- `digit_sum_span`
- `avg_repetition`
- `repetition_span`

These were computed across the same scalar state represented simultaneously in bases 2 through 16.

---

## First output

Run command:

```bash id="37ehbb"
python experiments/logistic_map_multibase_v0.py

Observed output:

Done. Wrote outputs/logistic_map_multibase_v0.csv

Sample rows from outputs/logistic_map_multibase_v0.csv

r	step	x	avg_digit_sum	digit_sum_span	avg_repetition	repetition_span

3.5	0	0.826940706691121516	45.53333333333333	42.0	0.048484848484848485	0.18181818181818182
3.5	1	0.500884210333256151	46.46666666666667	45.0	0.04848484848484848	0.18181818181818182
3.5	2	0.874997223405763071	47.733333333333334	43.0	0.06060606060606061	0.18181818181818182
3.5	3	0.382819842525150937	47.733333333333334	46.0	0.04242424242424243	0.18181818181818182


Immediate observation

At r = 3.5, the logistic map falls into a clear period-4 cycle.

The extracted Omniabase signatures repeat with the same cycle, showing that the method is not producing arbitrary noise. It is tracking regime structure in a representation-sensitive way.


---

Experiment 2 — Regime summary across coarse r values

Purpose

The second step was to summarize each regime rather than inspect only raw rows.

This was done to test whether Omniabase signatures separate dynamical regimes at the level of regime-wide statistics.

Run command:

python experiments/analyze_logistic_map_multibase_v0.py

Observed console output:

------------------------------------------------------------
r = 3.50
 n_steps: 200
 unique_states_rounded_12: 4
 x_std: 0.207851609139
 x_mean_abs_step_diff: 0.320490074258
 avg_digit_sum_std: 0.982061324177
 avg_digit_sum_mean_abs_step_diff: 1.516666666667
 digit_sum_span_std: 1.639359631075
 avg_repetition_std: 0.006659775084
 repetition_span_std: 0.000000000000
------------------------------------------------------------
r = 3.55
 n_steps: 200
 unique_states_rounded_12: 8
 x_std: 0.210459521360
 x_mean_abs_step_diff: 0.268735503061
 avg_digit_sum_std: 1.071649170425
 avg_digit_sum_mean_abs_step_diff: 1.488442211055
 digit_sum_span_std: 2.149273132945
 avg_repetition_std: 0.005574542618
 repetition_span_std: 0.040600109033
------------------------------------------------------------
r = 3.60
 n_steps: 200
 unique_states_rounded_12: 200
 x_std: 0.212003732688
 x_mean_abs_step_diff: 0.213969512392
 avg_digit_sum_std: 1.206263884323
 avg_digit_sum_mean_abs_step_diff: 1.341172529313
 digit_sum_span_std: 3.166348448924
 avg_repetition_std: 0.007629551468
 repetition_span_std: 0.051910609322
------------------------------------------------------------
r = 3.70
 n_steps: 200
 unique_states_rounded_12: 200
 x_std: 0.224647953255
 x_mean_abs_step_diff: 0.245803926038
 avg_digit_sum_std: 1.107063462499
 avg_digit_sum_mean_abs_step_diff: 1.258266331658
 digit_sum_span_std: 3.522641054663
 avg_repetition_std: 0.008453472093
 repetition_span_std: 0.063231454558
------------------------------------------------------------
r = 3.80
 n_steps: 200
 unique_states_rounded_12: 200
 x_std: 0.246440265780
 x_mean_abs_step_diff: 0.281898517228
 avg_digit_sum_std: 1.238426037355
 avg_digit_sum_mean_abs_step_diff: 1.402445561139
 digit_sum_span_std: 3.744111376548
 avg_repetition_std: 0.008594248464
 repetition_span_std: 0.060144574932
------------------------------------------------------------
r = 3.90
 n_steps: 200
 unique_states_rounded_12: 200
 x_std: 0.269476902677
 x_mean_abs_step_diff: 0.315144170792
 avg_digit_sum_std: 1.264213854117
 avg_digit_sum_mean_abs_step_diff: 1.455611390285
 digit_sum_span_std: 3.504812405821
 avg_repetition_std: 0.008298758838
 repetition_span_std: 0.065842183350
------------------------------------------------------------
r = 4.00
 n_steps: 200
 unique_states_rounded_12: 200
 x_std: 0.291776964893
 x_mean_abs_step_diff: 0.342921949514
 avg_digit_sum_std: 1.159385552351
 avg_digit_sum_mean_abs_step_diff: 1.353366834171
 digit_sum_span_std: 3.516086318622
 avg_repetition_std: 0.009497486801
 repetition_span_std: 0.066465369614
------------------------------------------------------------
Done. Wrote outputs/logistic_map_multibase_v0_summary.csv

Condensed regime summary

r	unique_states	x_std	avg_digit_sum_std	digit_sum_span_std	repetition_span_std

3.5	4	0.2078516	0.9820613	1.6393596	0.0000000
3.55	8	0.2104595	1.0716491	2.1492731	0.0406001
3.6	200	0.2120037	1.2062638	3.1663484	0.0519106
3.7	200	0.2246479	1.1070634	3.5226410	0.0632314
3.8	200	0.2464402	1.2384260	3.7441113	0.0601445
3.9	200	0.2694769	1.2642138	3.5048124	0.0658421
4.0	200	0.2917769	1.1593855	3.5160863	0.0664653


Main result of Experiment 2

The Omniabase signatures do not saturate when the simple unique_states count saturates.

From r = 3.6 onward, unique_states_rounded_12 stays at 200, but the multi-base signatures continue to move.

This is important because it suggests that Omniabase is not merely tracking obvious periodicity. It is still extracting differentiating structure inside already-chaotic regimes.


---

Experiment 3 — Fine-grained transition scan around the bifurcation region

Purpose

The third step was the real transition test.

Instead of checking only coarse regime differences, the experiment densified r around the critical transition region:

from 3.540 to 3.610

step size: 0.002


This was designed to answer the key question:

Does Omniabase amplify transition boundaries more clearly than standard simple statistics such as x_std?

Run command:

python experiments/logistic_map_regime_scan_v1.py

Observed output:

Done. Wrote outputs/logistic_map_regime_scan_v1.csv

Full transition scan summary

r	unique_states	x_std	avg_digit_sum_std	digit_sum_span_std	avg_repetition_std	repetition_span_std

3.540	4	0.20914972	0.99343399	1.81231895	0.00755358	0.00000000
3.542	4	0.20930776	1.00697567	1.83425734	0.00760451	0.00000000
3.544	8	0.20963384	1.03756857	1.95400230	0.00657929	0.02682977
3.546	8	0.20980481	1.04944122	2.01633950	0.00612185	0.03531086
3.548	8	0.20997787	1.05943615	2.07228738	0.00586937	0.04060010
3.550	8	0.21015307	1.07164917	2.14927313	0.00557454	0.04060010
3.552	8	0.21033045	1.08272547	2.19730030	0.00529528	0.04060010
3.554	8	0.21051004	1.09650000	2.27211355	0.00511528	0.04060010
3.556	8	0.21069189	1.10777555	2.33304522	0.00515152	0.04060010
3.558	8	0.21087602	1.12196024	2.40870814	0.00550428	0.04060010
3.560	8	0.21106250	1.13783457	2.47853283	0.00595300	0.04060010
3.562	8	0.21125134	1.15560942	2.58069757	0.00654131	0.04060010
3.564	8	0.21144259	1.17195705	2.65922333	0.00713781	0.04060010
3.566	16	0.21153139	1.19256910	2.84650630	0.00762145	0.04944882
3.568	243	0.21155990	1.19934251	2.92055620	0.00762181	0.05284358
3.570	250	0.21160416	1.19665798	2.95155107	0.00771809	0.05293208
3.572	250	0.21163155	1.20573733	3.01691285	0.00770542	0.05364175
3.574	250	0.21165431	1.18957448	2.93297598	0.00752763	0.05193635
3.576	250	0.21168170	1.18880622	2.97305942	0.00769351	0.05187424
3.578	250	0.21172159	1.18247012	2.94635156	0.00768291	0.05139884
3.580	250	0.21176161	1.19830848	3.03157204	0.00774635	0.05141011
3.582	250	0.21180295	1.18131377	3.01168340	0.00759908	0.04996256
3.584	250	0.21184699	1.19532464	3.06421584	0.00742183	0.04961726
3.586	250	0.21189396	1.20817340	3.12579133	0.00746654	0.04892404
3.588	250	0.21194285	1.19946821	3.13632946	0.00757279	0.04899385
3.590	250	0.21199342	1.19958744	3.15523910	0.00761265	0.04953935
3.592	250	0.21204689	1.20015501	3.16104764	0.00741270	0.05141206
3.594	250	0.21210166	1.19163618	3.12071833	0.00735870	0.05151515
3.596	250	0.21216010	1.18780287	3.14652433	0.00739818	0.05151515
3.598	250	0.21221976	1.19472659	3.17646698	0.00753696	0.05151515
3.600	250	0.21228227	1.20626388	3.16634845	0.00762955	0.05191061
3.602	250	0.21234720	1.19448375	3.14923145	0.00763863	0.05193420
3.604	250	0.21241470	1.19069150	3.15838081	0.00751998	0.05193420
3.606	250	0.21248464	1.20455015	3.20815454	0.00754876	0.05191061
3.608	250	0.21255755	1.18378524	3.13627581	0.00742512	0.05202450
3.610	250	0.21263155	1.19828552	3.19794033	0.00738670	0.05215007



---

Main result of Experiment 3

Transition 1: period-4 to period-8

At:

r = 3.542 -> unique_states = 4

r = 3.544 -> unique_states = 8


The standard scalar statistic x_std changes only weakly:

0.20930776 -> 0.20963384


But repetition_span_std jumps from:

0.00000000

to 0.02682977


This means Omniabase detects a clean structural break where the visible scalar variance changes only minimally.

Transition 2: pre-chaotic to chaotic regime

Around:

r = 3.564 -> unique_states = 8

r = 3.566 -> unique_states = 16

r = 3.568 -> unique_states = 243


Again, x_std remains almost flat:

0.21144259

0.21153139

0.21155990


But digit_sum_span_std rises much more clearly:

2.65922333

2.84650630

2.92055620


This is one of the strongest results so far.

It suggests that Omniabase signatures may act as regime-transition amplifiers even when simple scalar statistics barely move.


---

Current conclusion

The current prototype has now established three things:

1. Multi-base signatures track periodic regime structure.


2. Multi-base signatures continue to differentiate chaotic regimes even after simple regime counters saturate.


3. At least some Omniabase signatures appear to amplify transition boundaries more sharply than standard scalar statistics such as x_std.



This does not yet prove a general theory.

But it is already enough to justify the next phase:

Omniabase may be useful as a coordinate-discovery and early-transition sensing layer, not only as a representation trick.


---

Next step

The next correct step is to compute delta sensitivity across the fine transition scan.

That will answer the harder question:

Does Omniabase detect transitions earlier, or merely more noisily?

The next analysis will compare the step-to-step change of:

x_std

digit_sum_span_std

repetition_span_std


to see which family of signals reacts earlier and more strongly near bifurcation boundaries.


---

Author

Massimiliano Brighindi

